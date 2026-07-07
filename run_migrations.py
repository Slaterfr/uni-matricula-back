import uuid
from sqlmodel import Session, select, text
from app.core.database import engine

def migrate():
    print("Iniciando migración de base de datos...")
    
    with Session(engine) as session:
        # 1. Crear tabla de roles (limpiando posibles conflictos previos)
        print("Limpiando tablas de roles si existían conflictos...")
        session.execute(text("ALTER TABLE users DROP COLUMN IF EXISTS role_id CASCADE;"))
        session.execute(text("DROP TABLE IF EXISTS roles CASCADE;"))
        session.commit()
        
        print("Creando tabla 'roles'...")
        session.execute(text("""
        CREATE TABLE IF NOT EXISTS roles (
            id UUID PRIMARY KEY,
            name VARCHAR(255) UNIQUE NOT NULL,
            description VARCHAR(255)
        );
        """))
        session.commit()

        # Sembrar roles básicos
        print("Sembrando roles por defecto ('admin', 'professor', 'student')...")
        roles_to_seed = ["admin", "professor", "student"]
        role_map = {}
        for role_name in roles_to_seed:
            res = session.execute(text("SELECT id FROM roles WHERE name = :name"), {"name": role_name}).first()
            if not res:
                role_id = uuid.uuid4()
                session.execute(text("INSERT INTO roles (id, name, description) VALUES (:id, :name, :desc)"), {
                    "id": role_id,
                    "name": role_name,
                    "desc": f"Rol de {role_name}"
                })
                session.commit()
                role_map[role_name] = role_id
                print(f"Rol '{role_name}' sembrado.")
            else:
                role_map[role_name] = res[0]

        # 2. Modificar tabla de usuarios para enlazar con roles
        print("Agregando columna 'role_id' a la tabla 'users'...")
        session.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS role_id UUID;"))
        session.commit()

        # Mapear roles antiguos en base al string de la columna 'role' si existe (haciendo cast de enum a text)
        try:
            # Comprobar si existe la columna antigua 'role'
            has_role_col = session.execute(text("""
                SELECT COUNT(*) FROM information_schema.columns 
                WHERE table_name='users' AND column_name='role';
            """)).first()[0] > 0
            
            if has_role_col:
                print("Migrando roles de usuarios existentes...")
                session.execute(text("""
                UPDATE users 
                SET role_id = (SELECT id FROM roles WHERE name = 'admin') 
                WHERE role_id IS NULL AND role::text = 'admin';
                """))
                session.execute(text("""
                UPDATE users 
                SET role_id = (SELECT id FROM roles WHERE name = 'professor') 
                WHERE role_id IS NULL AND role::text = 'professor';
                """))
                session.execute(text("""
                UPDATE users 
                SET role_id = (SELECT id FROM roles WHERE name = 'student') 
                WHERE role_id IS NULL AND (role::text = 'student' OR role IS NULL);
                """))
                session.commit()
        except Exception as e:
            session.rollback()
            print(f"Nota: No se pudieron migrar los roles antiguos (se continuará sin migración): {e}")

        # Asignar rol por defecto a cualquier usuario que aún no lo tenga
        session.execute(text("UPDATE users SET role_id = (SELECT id FROM roles WHERE name = 'student') WHERE role_id IS NULL;"))
        session.commit()

        # Establecer role_id como NOT NULL y agregar FK
        print("Estableciendo restricciones de claves foráneas en 'users'...")
        session.execute(text("ALTER TABLE users ALTER COLUMN role_id SET NOT NULL;"))
        try:
            session.execute(text("ALTER TABLE users ADD CONSTRAINT fk_users_roles FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE RESTRICT;"))
            session.commit()
        except Exception as e:
            session.rollback()
            print(f"Clave foránea 'fk_users_roles' ya existe o falló: {e}")

        # Eliminar columna antigua 'role'
        try:
            session.execute(text("ALTER TABLE users DROP COLUMN IF EXISTS role;"))
            session.commit()
        except Exception as e:
            session.rollback()
            print(f"No se pudo eliminar columna 'role': {e}")

        # 3. Crear tabla de períodos
        print("Creando tabla 'periods'...")
        session.execute(text("""
        CREATE TABLE IF NOT EXISTS periods (
            id UUID PRIMARY KEY,
            name VARCHAR(255) UNIQUE NOT NULL,
            is_active BOOLEAN NOT NULL DEFAULT TRUE
        );
        """))
        session.commit()

        # Verificar si hay al menos un período activo, sino crearlo
        p_active = session.execute(text("SELECT id FROM periods WHERE is_active = TRUE")).first()
        if not p_active:
            default_p_id = uuid.uuid4()
            session.execute(text("INSERT INTO periods (id, name, is_active) VALUES (:id, 'I 2026', TRUE)"), {"id": default_p_id})
            session.commit()
            print("Período inicial 'I 2026' sembrado y activado.")
            p_active_id = default_p_id
        else:
            p_active_id = p_active[0]

        # 4. Modificar tabla de matrículas ('enrollments')
        print("Agregando columnas 'period_id' y 'grade' a 'enrollments'...")
        session.execute(text("ALTER TABLE enrollments ADD COLUMN IF NOT EXISTS period_id UUID;"))
        session.execute(text("ALTER TABLE enrollments ADD COLUMN IF NOT EXISTS grade DOUBLE PRECISION;"))
        session.commit()

        # Migrar datos de períodos en matrículas
        try:
            # Comprobar si existe la columna antigua 'period'
            has_period_col = session.execute(text("""
                SELECT COUNT(*) FROM information_schema.columns 
                WHERE table_name='enrollments' AND column_name='period';
            """)).first()[0] > 0
            
            if has_period_col:
                print("Migrando períodos de matrículas existentes...")
                res_periods = session.execute(text("SELECT DISTINCT period FROM enrollments WHERE period_id IS NULL")).all()
                for row in res_periods:
                    period_str = row[0]
                    if not period_str:
                        continue
                    # Obtener o crear período
                    p_exists = session.execute(text("SELECT id FROM periods WHERE name = :name"), {"name": period_str}).first()
                    if not p_exists:
                        p_id = uuid.uuid4()
                        session.execute(text("INSERT INTO periods (id, name, is_active) VALUES (:id, :name, TRUE)"), {"id": p_id, "name": period_str})
                        session.commit()
                        print(f"Período '{period_str}' creado durante migración.")
                    else:
                        p_id = p_exists[0]
                    
                    # Actualizar
                    session.execute(text("UPDATE enrollments SET period_id = :p_id WHERE period = :period_str"), {"p_id": p_id, "period_str": period_str})
                    session.commit()
        except Exception as e:
            session.rollback()
            print(f"Nota: No se pudieron migrar los períodos antiguos: {e}")

        # Asignar período por defecto a matrículas que no lo tengan
        session.execute(text("UPDATE enrollments SET period_id = :p_active_id WHERE period_id IS NULL"), {"p_active_id": p_active_id})
        session.commit()

        # Establecer restricciones en enrollments
        print("Estableciendo restricciones de claves foráneas en 'enrollments'...")
        session.execute(text("ALTER TABLE enrollments ALTER COLUMN period_id SET NOT NULL;"))
        try:
            session.execute(text("ALTER TABLE enrollments ADD CONSTRAINT fk_enrollments_periods FOREIGN KEY (period_id) REFERENCES periods(id) ON DELETE RESTRICT;"))
            session.commit()
        except Exception as e:
            session.rollback()
            print(f"Clave foránea 'fk_enrollments_periods' ya existe o falló: {e}")

        try:
            session.execute(text("ALTER TABLE enrollments DROP COLUMN IF EXISTS period;"))
            session.commit()
        except Exception as e:
            session.rollback()
            print(f"No se pudo eliminar columna 'period': {e}")

        # 5. Modificar tabla de cursos ('courses')
        print("Agregando columna 'max_capacity' a 'courses'...")
        session.execute(text("ALTER TABLE courses ADD COLUMN IF NOT EXISTS max_capacity INTEGER DEFAULT 30;"))
        session.commit()

        # 6. Crear tabla de pagos ('payments')
        print("Creando tabla 'payments'...")
        session.execute(text("""
        CREATE TABLE IF NOT EXISTS payments (
            id UUID PRIMARY KEY,
            student_id UUID NOT NULL REFERENCES students(id) ON DELETE CASCADE,
            amount DOUBLE PRECISION NOT NULL,
            status VARCHAR(50) NOT NULL DEFAULT 'pending',
            date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
        );
        """))
        session.commit()

    print("Base de datos migrada exitosamente.")

if __name__ == "__main__":
    migrate()

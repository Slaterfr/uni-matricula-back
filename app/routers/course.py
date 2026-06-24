import uuid
from typing import List
from fastapi import APIRouter, Depends, status
from sqlmodel import Session

from app.core.database import get_db
from app.core.deps import RoleChecker, get_current_user
from app.schemas.course import CourseCreate, CourseUpdate, CourseResponse
from app.services import course as course_service

router = APIRouter()

# Restricciones de roles
admin_required = Depends(RoleChecker(["admin"]))
any_user = Depends(get_current_user)

@router.post("", response_model=CourseResponse, status_code=status.HTTP_201_CREATED, dependencies=[admin_required])
def create_new_course(
    course_in: CourseCreate,
    db: Session = Depends(get_db)
):
    """
    Crea un nuevo curso en la universidad.
    Solo accesible por administradores.
    """
    course = course_service.create_course(db, course_in=course_in)
    return course_service.to_course_response(course)

@router.get("", response_model=List[CourseResponse], dependencies=[any_user])
def read_courses(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Obtiene la lista de cursos ofertados.
    Accesible por cualquier usuario autenticado (estudiantes, profesores y administradores).
    """
    courses = course_service.get_all_courses(db, skip=skip, limit=limit)
    return [course_service.to_course_response(c) for c in courses]

@router.get("/{course_id}", response_model=CourseResponse, dependencies=[any_user])
def read_course_detail(
    course_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    """
    Obtiene el detalle de un curso específico.
    Accesible por cualquier usuario autenticado.
    """
    course = course_service.get_course_by_id(db, course_id=course_id)
    return course_service.to_course_response(course)

@router.put("/{course_id}", response_model=CourseResponse, dependencies=[admin_required])
def update_course_detail(
    course_id: uuid.UUID,
    course_in: CourseUpdate,
    db: Session = Depends(get_db)
):
    """
    Actualiza la información de un curso.
    Solo accesible por administradores.
    """
    updated = course_service.update_course(db, course_id=course_id, course_in=course_in)
    return course_service.to_course_response(updated)

@router.delete("/{course_id}", response_model=CourseResponse, dependencies=[admin_required])
def delete_course_by_id(
    course_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    """
    Elimina un curso.
    Solo accesible por administradores.
    """
    deleted = course_service.delete_course(db, course_id=course_id)
    return course_service.to_course_response(deleted)

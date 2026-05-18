from aiogram.dispatcher.filters.state import State, StatesGroup


class RoleSelectState(StatesGroup):
    role = State()


class UstuzLessonState(StatesGroup):
    title = State()
    description = State()
    file = State()


class UstuzAssignmentState(StatesGroup):
    lesson_id = State()
    title = State()
    description = State()
    deadline = State()


class UstuzGradeState(StatesGroup):
    submission_id = State()
    grade = State()
    feedback = State()


class ShogirdSubmitState(StatesGroup):
    assignment_id = State()
    answer = State()

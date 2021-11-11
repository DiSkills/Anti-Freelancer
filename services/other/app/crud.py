from app.feedback.schemas import CreateFeedback
from app.models import Feedback
from crud import CRUD


class FeedbackCRUD(CRUD[Feedback, CreateFeedback, CreateFeedback]):
    """ Feedback CRUD """
    pass


feedback_crud = FeedbackCRUD(Feedback)

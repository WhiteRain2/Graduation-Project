from demo.models import Community, Student
from demo.models.message import Message


class MessageRepository:
    @staticmethod
    def store_or_handle_message(community_id, student_id, text, created_at):
        if community_id != '0':
            community = Community.objects.get(id=community_id)
            student = Student.objects.get(student_id=student_id)
            message = Message.objects.create(
                community=community,
                sender=student,
                text=text,
                created_at=created_at
            )
        else:
            student = Student.objects.get(student_id=student_id)
            message = Message.objects.create(
                community=None,
                sender=student,
                text=text,
                created_at=created_at
            )
        return message

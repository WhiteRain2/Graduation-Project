# demo/models/__init__.py

from .student import Student
from .community import Community
from .course import Course
# 明确列出关系模块所有导出的模型
from .relations import CommunityMember,CommunityCompletedCourse,CommunityWishCourse,CompletedCourse,WishCourse

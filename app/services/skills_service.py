from app.models.skills import Skill
from app.models.user import User
from app.repository.skills_repo import SkillRepository as SkillRepo



class SkillService:
    def __init__(self, db):
        self.db = db
        self.skill_repo = SkillRepo(db)

    def create_skill(self, name: str, admin: User) -> Skill:
        if not admin.is_admin:
            raise PermissionError("Only admins can create skills")
        
        existing_skill = self.skill_repo.get_by_name(name)
        if existing_skill:
            raise ValueError("Skill with this name already exists")

        return self.skill_repo.create_skill(name)
    
    def list_skills(self) -> list[Skill]:
        return self.skill_repo.get_all_skills()
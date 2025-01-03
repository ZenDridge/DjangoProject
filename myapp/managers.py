from django.contrib.auth.models import BaseUserManager

class UserMgr(BaseUserManager):
    def create_user(self, email, first_name, middle_name, last_name, sid, pwd=None):
        if not email:
            raise ValueError('Email required')
        if not sid:
            raise ValueError('Student ID is required')

        user = self.model(
            email=self.normalize_email(email),
            first_name=first_name,
            middle_name=middle_name,
            last_name=last_name,
            sid=sid,
            active=True
        )
        user.set_password(pwd)  # Ensures the password is hashed
        user.save(using=self._db)
        return user

    def create_staff(self, email, first_name, middle_name, last_name, sid, pwd):
        user = self.create_user(email, first_name, middle_name, last_name, sid, pwd)
        user.staff = True
        user.save(using=self._db)
        return user

    def create_superuser(self, email, first_name, middle_name, last_name, sid, pwd):
        user = self.create_user(email, first_name, middle_name, last_name, sid, pwd)
        user.staff = True
        user.admin = True
        user.save(using=self._db)
        return user

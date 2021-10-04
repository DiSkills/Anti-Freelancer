from passlib.context import CryptContext

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


def get_password_hash(password: str) -> str:
    """
        Get password hash
        :param password: Password
        :type password: str
        :return: Hash
        :rtype: str
    """
    return pwd_context.hash(password)

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


def verify_password_hash(password: str, hash_password: str) -> bool:
    """
        Verify password
        :param password: Password
        :type password: str
        :param hash_password: Hash password
        :type hash_password: str
        :return: Passwords match?
        :rtype: bool
    """
    return pwd_context.verify(password, hash_password)

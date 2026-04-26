from services.user_servic import creatin_new_user, get_user_by_login_and_password
import asyncio


async def main() -> None:
    print(await creatin_new_user("misha", "sosal?", "yes", "user"))
    print(await creatin_new_user("vania", "sosal?", "no", "user"))
    print(get_user_by_login_and_password("sosal?", "no"))
    print(get_user_by_login_and_password("sosal?", "yes"))


if __name__ == "__main__":
    asyncio.run(main())

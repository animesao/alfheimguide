from .verification import Verification, VerificationView, VerifyMainMenuView


async def setup(bot):
    await bot.add_cog(Verification(bot))

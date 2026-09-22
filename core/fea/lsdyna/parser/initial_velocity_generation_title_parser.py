from .initial_velocity_generation_parser import InitialVelocityGenerationParser


class InitialVelocityGenerationTitleParser(InitialVelocityGenerationParser):
    def __init__(self):
        super().__init__(title=True)

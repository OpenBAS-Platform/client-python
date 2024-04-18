from pyobas.contracts.contract_utils import (
    ContractCardinality,
    ContractVariable,
    VariableType,
)

USER = "user"
EXERCISE = "exercise"
TEAMS = "teams"
COMCHECK = "comcheck"
PLAYER_URI = "player_uri"
CHALLENGES_URI = "challenges_uri"
SCOREBOARD_URI = "scoreboard_uri"
LESSONS_URI = "lessons_uri"


class VariableHelper:
    @staticmethod
    def user_variable():
        return ContractVariable(
            key=USER,
            label="User that will receive the injection",
            type=VariableType.String,
            cardinality=ContractCardinality.One,
            children=[
                ContractVariable(
                    key=USER + ".id",
                    label="Id of the user in the platform",
                    type=VariableType.String,
                    cardinality=ContractCardinality.One,
                ),
                ContractVariable(
                    key=USER + ".email",
                    label="Email of the user",
                    type=VariableType.String,
                    cardinality=ContractCardinality.One,
                ),
                ContractVariable(
                    key=USER + ".firstname",
                    label="Firstname of the user",
                    type=VariableType.String,
                    cardinality=ContractCardinality.One,
                ),
                ContractVariable(
                    key=USER + ".lastname",
                    label="Lastname of the user",
                    type=VariableType.String,
                    cardinality=ContractCardinality.One,
                ),
                ContractVariable(
                    key=USER + ".lang",
                    label="Lang of the user",
                    type=VariableType.String,
                    cardinality=ContractCardinality.One,
                ),
            ],
        )

    @staticmethod
    def exercise_variable():
        return ContractVariable(
            key=EXERCISE,
            label="Exercise of the current injection",
            type=VariableType.Object,
            cardinality=ContractCardinality.One,
            children=[
                ContractVariable(
                    key=EXERCISE + ".id",
                    label="Id of the exercise in the platform",
                    type=VariableType.String,
                    cardinality=ContractCardinality.One,
                ),
                ContractVariable(
                    key=EXERCISE + ".name",
                    label="Name of the exercise",
                    type=VariableType.String,
                    cardinality=ContractCardinality.One,
                ),
                ContractVariable(
                    key=EXERCISE + ".description",
                    label="Description of the exercise",
                    type=VariableType.String,
                    cardinality=ContractCardinality.One,
                ),
            ],
        )

    @staticmethod
    def team_variable():
        return ContractVariable(
            key=TEAMS,
            label="List of team name for the injection",
            type=VariableType.String,
            cardinality=ContractCardinality.Multiple,
        )

    @staticmethod
    def uri_variables():
        return [
            ContractVariable(
                key=PLAYER_URI,
                label="Player interface platform link",
                type=VariableType.String,
                cardinality=ContractCardinality.One,
            ),
            ContractVariable(
                key=CHALLENGES_URI,
                label="Challenges interface platform link",
                type=VariableType.String,
                cardinality=ContractCardinality.One,
            ),
            ContractVariable(
                key=SCOREBOARD_URI,
                label="Scoreboard interface platform link",
                type=VariableType.String,
                cardinality=ContractCardinality.One,
            ),
            ContractVariable(
                key=LESSONS_URI,
                label="Lessons learned interface platform link",
                type=VariableType.String,
                cardinality=ContractCardinality.One,
            ),
        ]

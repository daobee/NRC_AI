"""
Battle trigger regression tests.

Covers:
1. ON_BATTLE_START is triggered once on battle entry.
2. ON_ALLY_COUNTER is triggered when a teammate successfully counters.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.models import Pokemon, Skill, BattleState, Type, SkillCategory
from src.effect_models import E, EffectTag, Timing, AbilityEffect
from src.battle import auto_switch, execute_full_turn


def make_skill(name, power=40, energy=0, skill_type=Type.NORMAL,
               category=SkillCategory.PHYSICAL, effects=None):
    return Skill(
        name=name,
        skill_type=skill_type,
        category=category,
        power=power,
        energy_cost=energy,
        effects=effects or [],
    )


def make_pokemon(name="test", hp=200, attack=100, defense=80,
                 spatk=80, spdef=80, speed=80, ptype=Type.NORMAL,
                 skills=None, ability="", energy=10):
    return Pokemon(
        name=name,
        pokemon_type=ptype,
        hp=hp,
        attack=attack,
        defense=defense,
        sp_attack=spatk,
        sp_defense=spdef,
        speed=speed,
        ability=ability,
        skills=skills or [],
        energy=energy,
    )


def test_battle_start_triggers_once():
    starter = make_pokemon(
        "starter",
        skills=[make_skill("strike")],
    )
    starter.ability_effects = [
        AbilityEffect(
            Timing.ON_BATTLE_START,
            [EffectTag(E.ABILITY_INCREMENT_COUNTER)],
        )
    ]
    other = make_pokemon("other", skills=[make_skill("guard")])
    state = BattleState(team_a=[starter], team_b=[other], current_a=0, current_b=0)

    auto_switch(state)
    auto_switch(state)

    assert state.counter_count_a == 1
    assert state.battle_start_effects_triggered is True


def test_ally_counter_triggers_allied_ability():
    attacker = make_pokemon(
        "attacker",
        speed=120,
        skills=[make_skill("strike", power=70, energy=0, skill_type=Type.FIRE)],
    )
    counter_user = make_pokemon(
        "counter_user",
        hp=220,
        speed=20,
        energy=0,
        skills=[
            make_skill(
                "guard_retaliate",
                power=0,
                energy=5,
                category=SkillCategory.DEFENSE,
                effects=[EffectTag(E.COUNTER_ATTACK)],
            )
        ],
    )
    ally = make_pokemon(
        "ally",
        energy=0,
        skills=[make_skill("support")],
    )
    ally.ability_effects = [
        AbilityEffect(
            Timing.ON_ALLY_COUNTER,
            [EffectTag(E.HEAL_ENERGY, {"amount": 1})],
        )
    ]
    state = BattleState(
        team_a=[attacker],
        team_b=[counter_user, ally],
        current_a=0,
        current_b=0,
    )

    execute_full_turn(state, (0,), (0,))

    assert ally.energy == 1


if __name__ == "__main__":
    test_battle_start_triggers_once()
    test_ally_counter_triggers_allied_ability()
    print("PASS: battle trigger regressions")

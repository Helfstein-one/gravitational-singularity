"""
Product entry points for gravitational_singularity CLI commands.
"""

from src.adapters.inbound.ast_search_cli import main as ast_search_main
from src.adapters.inbound.doctor_cli import main as doctor_main

def ast_search_cli():
    return ast_search_main()

def doctor_cli():
    return doctor_main()

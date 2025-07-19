

# doctor (selector function)
def medico(usuario_ativo):
    """
    Retrieves the Medico (Doctor) object associated with an active user.

    This function acts as a selector to get the specific doctor profile linked
    to the currently authenticated user. It assumes a one-to-one or one-to-many
    relationship where a user can be associated with one or more doctor profiles,
    and it retrieves the first one found.

    Security: Only returns doctor objects for users with is_medico flag set,
    providing role-based access control for medical functions.

    Critique:
    - The function name `medico` is in Portuguese. It should be `get_doctor` or
      `select_doctor` for consistency with English comments.
    - The `else: pass` statement is redundant and can be removed.
    - The function assumes `usuario_ativo.medicos.first()` will always return
      a valid `Medico` object if `is_medico` is True. It might be more robust
      to handle cases where `medicos.first()` returns `None` (e.g., if the
      relationship is broken or not yet established).

    Args:
        # active_user
        usuario_ativo (User): The currently authenticated user object.

    Returns:
        Medico: The `Medico` object associated with the user, or `None` if
                the user is not a doctor or no doctor profile is found.
    """
    if usuario_ativo.is_medico:
        # doctor (get first associated doctor profile)
        medico = usuario_ativo.medicos.first()
        return medico
    else:
        pass

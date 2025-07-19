import re


# is_cpf_valid
def isCpfValid(cpf):
    """
    Validates Brazilian CPF (Cadastro de Pessoas Físicas) number.
    
    CPF is the Brazilian individual taxpayer registry, equivalent to SSN in the US.
    This function implements the official CPF validation algorithm using check digits.
    
    Security: Proper CPF validation prevents invalid IDs from being stored,
    ensuring data integrity for patient identification in the medical system.
    
    Args:
        cpf (str): CPF number as string, may contain formatting characters
        
    Returns:
        bool: True if CPF is valid, False otherwise
    """
    # Check if type is str
    if not isinstance(cpf, str):
        return False

    # Remove some unwanted characters (dots, dashes, spaces)
    cpf = re.sub("[^0-9]", "", cpf)

    # Checks if string has 11 characters
    if len(cpf) != 11:
        return False

    # sum_total
    sum = 0
    # weight_multiplier
    weight = 10

    # Calculating the first CPF check digit using weighted sum algorithm
    for n in range(9):
        sum = sum + int(cpf[n]) * weight
        # Decrement weight
        weight = weight - 1

    # verifying_digit
    verifyingDigit = 11 - sum % 11

    if verifyingDigit > 9:
        # first_verifying_digit
        firstVerifyingDigit = 0
    else:
        # first_verifying_digit
        firstVerifyingDigit = verifyingDigit

    # Calculating the second check digit of CPF
    # sum_total
    sum = 0
    # weight_multiplier
    weight = 11
    for n in range(10):
        sum = sum + int(cpf[n]) * weight
        # Decrement weight
        weight = weight - 1

    # verifying_digit
    verifyingDigit = 11 - sum % 11

    if verifyingDigit > 9:
        # second_verifying_digit
        secondVerifyingDigit = 0
    else:
        # second_verifying_digit
        secondVerifyingDigit = verifyingDigit

    # Validate both check digits match the last two digits of CPF
    if cpf[-2:] == "%s%s" % (firstVerifyingDigit, secondVerifyingDigit):
        return True
    return False


# is_cnpj_valid
def isCnpjValid(cnpj):
    """
    Validates Brazilian CNPJ (Cadastro Nacional da Pessoa Jurídica) number.
    
    CNPJ is the Brazilian company taxpayer registry, used for business identification.
    This function implements the official CNPJ validation algorithm using check digits.
    
    Security: Proper CNPJ validation ensures clinic registration numbers are valid,
    maintaining data integrity for medical facility identification.
    
    Args:
        cnpj (str): CNPJ number as string, may contain formatting characters
        
    Returns:
        bool: True if CNPJ is valid, False otherwise
    """
    # Check if type is str
    if not isinstance(cnpj, str):
        return False

    # Remove some unwanted characters (dots, dashes, slashes, spaces)
    # Note: Variable name should be 'cnpj' not 'cpf' for clarity
    cpf = re.sub("[^0-9]", "", cnpj)

    # Checks if string has 14 characters (CNPJ length)
    if len(cpf) != 14:
        return False

    # sum_total
    sum = 0
    # weight_sequence for first check digit
    weight = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]

    # Calculating the first CNPJ check digit
    for n in range(12):
        # value
        value = int(cpf[n]) * weight[n]
        sum = sum + value

    # verifying_digit
    verifyingDigit = sum % 11

    if verifyingDigit < 2:
        # first_verifying_digit
        firstVerifyingDigit = 0
    else:
        # first_verifying_digit
        firstVerifyingDigit = 11 - verifyingDigit

    # Calculating the second check digit of CNPJ
    # sum_total
    sum = 0
    # weight_sequence for second check digit
    weight = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    for n in range(13):
        sum = sum + int(cpf[n]) * weight[n]

    # verifying_digit
    verifyingDigit = sum % 11

    if verifyingDigit < 2:
        # second_verifying_digit
        secondVerifyingDigit = 0
    else:
        # second_verifying_digit
        secondVerifyingDigit = 11 - verifyingDigit

    # Validate both check digits match the last two digits of CNPJ
    if cpf[-2:] == "%s%s" % (firstVerifyingDigit, secondVerifyingDigit):
        return True
    return False
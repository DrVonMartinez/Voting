import numpy as np
import scipy


def __non_linear(value: np.ndarray, min_value: float, max_value: float) -> np.ndarray:
    numerator = np.log(max_value - min_value) - np.log(max_value - value)
    denominator = np.log(max_value - min_value)
    index = numerator / denominator
    index[index > 1] = 1
    return index


def __linear(value: np.ndarray, min_value: float, max_value: float) -> np.ndarray:
    numerator = value - min_value
    denominator = max_value - min_value
    index = numerator / denominator
    index[index > 1] = 1
    return index


def __health_index(health_value: np.ndarray) -> np.ndarray:
    max_age_expected = 85
    min_age_expected = 0
    return __linear(health_value, min_age_expected, max_age_expected)


def __expected_education_index(expected_education_value: np.ndarray) -> np.ndarray:
    min_expected_years = 0
    max_expected_years = 18
    return __linear(expected_education_value, min_expected_years, max_expected_years)


def __mean_education_index(mean_education_value: np.ndarray) -> np.ndarray:
    min_mean_years = 0
    max_mean_years = 15
    return __linear(mean_education_value, min_mean_years, max_mean_years)


def __literacy_education_index(adult_literacy_value):
    min_literacy_percent = 0
    max_literacy_percent = 1
    return __non_linear(adult_literacy_value, min_literacy_percent, max_literacy_percent)


def __educational_enrollment_index(education_enrollment_value):
    min_enrollment_percent = 0
    max_enrollment_percent = 1
    return __non_linear(education_enrollment_value, min_enrollment_percent, max_enrollment_percent)


def __income_index(income_value: np.ndarray) -> np.ndarray:
    min_income_per_capita = 100
    max_income_per_capita = 75000
    return __linear(income_value, min_income_per_capita, max_income_per_capita)


def HDI(health: np.ndarray, exp_education: np.ndarray, mean_education: np.ndarray, income: np.ndarray) -> np.ndarray:
    """
    Human Development Index:
    "Single index measure to capture 3 key dimensions of human development"
    https://ourworldindata.org/human-development-index
    :param health:
    :param exp_education:
    :param mean_education:
    :param income:
    :return:
    """
    health_index = __health_index(health)
    expected_education = __expected_education_index(exp_education)
    mean_education = __mean_education_index(mean_education)
    education_index = (expected_education + mean_education) / 2
    income_index = __income_index(income)
    return np.power(health_index * education_index * income_index, 1 / 3)


def HIHD(health: np.ndarray, adult_literacy: np.ndarray, ed_enrollment: np.ndarray, income: np.ndarray) -> np.ndarray:
    """
    Historical Index of Human Development
    "Single index measure to capture 3 key dimensions of human development"
    https://ourworldindata.org/human-development-index
    :param health:
    :param adult_literacy:
    :param ed_enrollment:
    :param income:
    :return:
    """
    health_index = __health_index(health)
    expected_education = __literacy_education_index(adult_literacy)
    mean_education = __educational_enrollment_index(ed_enrollment)
    education_index = (expected_education + mean_education) / 2
    education_index[education_index > 1] = 1
    income_index = __income_index(income)
    return np.power(health_index * education_index * income_index, 1 / 3)

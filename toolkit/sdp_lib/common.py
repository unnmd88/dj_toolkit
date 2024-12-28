from datetime import datetime as dt


def set_curr_datetime(sep: str = ':') -> str:
    """
    Возвращает текущую дату и время
    :param sep: разделитель между датой и временем
    :return: отформатированная строка с датой и временем
    """

    return dt.today().strftime(f"%Y-%m-%d %H{sep}%M{sep}%S")
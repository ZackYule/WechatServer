def singleton(cls):
    """
    单例模式装饰器。

    当应用这个装饰器到一个类上时，确保这个类只有一个实例。
    无论这个类被实例化多少次，都只返回第一次创建的实例。

    :param cls: 要应用单例模式的类
    :return: 类的单一实例
    """
    instances = {}

    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return get_instance

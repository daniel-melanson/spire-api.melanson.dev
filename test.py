import re


def re_override_factory(*args: tuple[str, str]):
    def f(x):
        for (pattern, replace) in args:
            if (match := re.match(pattern, x)):
                if x is None:
                    x = None
                else:
                    for replace_match in re.finditer(r"\$(\d+)", replace):
                        group_number = replace_match.group(1)
                        replacing_text = match.group()
                        


        return x

    return f


override = re_override_factory((r"^\d$", "$0.00"))

print(override("3"))
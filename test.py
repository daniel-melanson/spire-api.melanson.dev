import re


def re_override_factory(*args: tuple[str, str]):
    def f(x):
        for (pattern, replace) in args:
            if match := re.match(pattern, x):
                if x is None:
                    x = None
                else:
                    offset = 0
                    for replace_match in re.finditer(r"\$(\d+)", replace):
                        group_number = replace_match.group(1)
                        inserting_text = match.group(int(group_number))

                        (low, high) = replace_match.span(0)
                        old = len(replace)
                        replace = replace[: offset + low] + inserting_text + replace[offset + high :]
                        offset += len(replace) - old

                    x = replace

        return x

    return f


override = re_override_factory((r"(\d) - (\d)", "$1.00 - $2.00"))

print(override("3 - 6"))

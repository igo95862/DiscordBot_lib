# File where I wrote functions that helped parse and make changes to multiple lines of code


def read_source_file(name: str)->str:
    f = open(name)
    s = f.read()
    f.close()
    return s


def save_as_new(text: str):
    f = open('./new.py', mode='w')
    f.write(text)
    f.close()


def find_brace_close_position(text: str, brace_start: int)->int:
    scope_level = 1
    position = brace_start + 1

    while scope_level > 0:
        char = text[position]
        if char == ')':
            scope_level -= 1
            if scope_level == 0:
                return position
        elif char == '(':
            scope_level += 1
        position += 1

    return position


test_fstring_convert = 'self.API_url + \'/webhooks/\' + str(webhook_id) + \'/\' + str(webhook_token)'


def replace_string_cat_to_fstring(source_code: str):
    code_fragments = []

    current_pos = 0
    for i, j in find_url_calls(source_code):
        code_fragments.append(source_code[current_pos:i+1])
        code_fragments.append(string_cat_to_fstring(source_code[i+1:j]))
        current_pos = j

    code_fragments.append(source_code[current_pos:])

    new_source = ''

    for s in code_fragments:
        new_source += s

    return new_source


def find_url_calls(original_text: str):
    start_pos = 0
    end_pos = 0
    while True:
        start_pos = original_text.find('return self.', end_pos)
        if start_pos < 0:
            break

        if original_text[start_pos+12] == '_':
            end_pos = start_pos + 1
            continue

        start_pos = original_text.find('(', start_pos)

        closing_brace = find_brace_close_position(original_text, start_pos)
        next_comma = original_text.find(',', start_pos)

        if next_comma < 0 or closing_brace < next_comma:
            end_pos = closing_brace
        else:
            end_pos = next_comma

        yield start_pos, end_pos


def string_cat_to_fstring(original_str: str)->str:
    tokens = original_str.split('+')
    new_string = 'f\''
    for t in tokens:
        if '\'' in t:
            # string
            new_string += t.strip().strip('\'')
        else:
            # value
            new_t = str(t).strip()

            if 'str(' in t:
                new_string += '{' + f'{new_t[4:-1]}' + '}'
            else:
                new_string += '{' + f'{new_t}' + '}'
    return new_string + '\''


def discordrest_to_discordbot_translate(discordrest_source_code: str):
    pass


def fetch_function_declaration_and_args(original_str: str):
    start_pos = 0
    end_pos = 0
    while True:
        start_pos = original_str.find('    def ', end_pos)
        if start_pos <= 0:
            break
        openning_brace = original_str.find('(', start_pos)
        closing_brace = find_brace_close_position(original_str, openning_brace)
        end_pos = closing_brace
        yield original_str[start_pos:closing_brace+1]

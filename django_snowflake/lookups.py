from django.db.models.fields.json import (
    HasKeyLookup, KeyTextTransform, KeyTransform,
)


def compile_json_path(key_transforms):
    json_path = ''
    for transform in key_transforms:
        try:
            idx = int(transform)
        except ValueError:  # non-integer
            # The first separator must be a colon, otherwise a period.
            separator = ':' if json_path == '' else '.'
            # Escape quotes to protect against SQL injection.
            transform = transform.replace('"', '\\"')
            json_path += f'{separator}"{transform}"'
        else:
            # An integer lookup is an array index.
            json_path += f'[{idx}]'
    # Escape percent literals since snowflake-connector-python uses
    # interpolation to bind parameters.
    return json_path.replace('%', '%%')


def key_text_transform(self, compiler, connection):
    lhs, params, key_transforms = self.preprocess_lhs(compiler, connection)
    json_path = compile_json_path(key_transforms)
    return f'{lhs}{json_path}::VARCHAR', tuple(params)


def has_key_lookup(self, compiler, connection):
    # Process JSON path from the left-hand side.
    if isinstance(self.lhs, KeyTransform):
        lhs, lhs_params, lhs_key_transforms = self.lhs.preprocess_lhs(
            compiler, connection
        )
        lhs_json_path = compile_json_path(lhs_key_transforms)
    else:
        lhs, lhs_params = self.process_lhs(compiler, connection)
        lhs_json_path = ''
    # Process JSON path from the right-hand side.
    rhs = self.rhs
    rhs_params = []
    if not isinstance(rhs, (list, tuple)):
        rhs = [rhs]
    rhs_json_paths = []
    for key in rhs:
        if isinstance(key, KeyTransform):
            *_, rhs_key_transforms = key.preprocess_lhs(compiler, connection)
        else:
            rhs_key_transforms = [key]
        *rhs_key_transforms, final_key = rhs_key_transforms
        rhs_json_path = compile_json_path(rhs_key_transforms)
        final_key = self.compile_json_path_final_key(final_key)
        # If this is the only key, the separator must be a colon.
        if rhs_json_path == '':
            final_key = final_key.replace('.', ':', 1)
        rhs_json_path += final_key
        rhs_json_paths.append(rhs_json_path)
    # Add condition for each key.
    if self.logical_operator:
        sql = f'IS_NULL_VALUE({lhs}{lhs_json_path}%s) IS NOT NULL'
        sql = "(%s)" % self.logical_operator.join(sql % path for path in rhs_json_paths)
    else:
        sql = f'IS_NULL_VALUE({lhs}{lhs_json_path}{rhs_json_paths[0]}) IS NOT NULL'
    return sql, tuple(lhs_params) + tuple(rhs_params)


def key_transform(self, compiler, connection):
    lhs, params, key_transforms = self.preprocess_lhs(compiler, connection)
    json_path = compile_json_path(key_transforms)
    return f'TO_JSON({lhs}{json_path})', tuple(params)


def register_lookups():
    HasKeyLookup.as_snowflake = has_key_lookup
    KeyTextTransform.as_snowflake = key_text_transform
    KeyTransform.as_snowflake = key_transform

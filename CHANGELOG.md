# Changelog

## 6.0.1 - Unreleased

- Fix crash creating virtual ``GeneratedField`` columns with a NUMBER type
  where the generated expression's inferred precision doesn't match the
  column's declared precision, e.g. when the expression involves arithmetic on
  NUMBER columns.

## 6.0 - 2025-12-05

Initial release for Django 6.0.x.

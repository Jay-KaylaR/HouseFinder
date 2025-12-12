from pathlib import Path
p = Path('properties/models.py')
if not p.exists():
    print('target file not found at', p.resolve())
    raise SystemExit(1)
s = p.read_text(encoding='utf-8')
# Fix the bad status default syntax
s_new = s.replace("status = models.CharField(max_length=20, choices=STATUS_CHOICES, **default='pending'**)",
              "status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')")
# Rename the second Property class to avoid name collision
s_new = s_new.replace('\nclass Property(models.Model):\n    STATUS_CHOICES = (', '\nclass PropertyExtended(models.Model):\n    STATUS_CHOICES = (')

if s == s_new:
    print('No changes necessary')
else:
    p.write_text(s_new, encoding='utf-8')
    print('models.py patched')

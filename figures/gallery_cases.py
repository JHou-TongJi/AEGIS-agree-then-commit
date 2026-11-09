"""The six real crops of Fig. 7 and what each one shows. Shared by the crop script and the
document build, so the table beneath the figure and the images cannot drift apart."""
CASES = [  # (condition, callout index, mechanism, rendering label)
 ('100_jpeg', 16, 'decimal point lost', '100 dpi, JPEG'),
 ('100_clean', 47, 'minus sign lost', '100 dpi, clean'),
 ('150_skew', 49, 'digit invented', '150 dpi, rotated'),
 ('150_blur', 46, 'zero read as one', '150 dpi, blurred'),
 ('100_skew', 1, 'digit substituted', '100 dpi, rotated'),
 ('300_skew', 7, 'two channels wrong and agreeing', '300 dpi, rotated'),
]

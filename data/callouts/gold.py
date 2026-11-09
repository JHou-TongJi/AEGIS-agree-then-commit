"""Gold values of the 54 measurement callouts on FE-0041 page 2, in the order of boxes.json
(panel p1..p6, then top-to-bottom, left-to-right). Transcribed by hand from a 600 dpi render,
cross-checked against an independent read at 600 dpi of each cropped callout."""
GOLD = ['1.4','1.3','1.6','1.0','1.0','1.0','1.0','0.7','0.6',
        '0.3','0.3','0.2','0.6','0.3','0.6','0.6','0.9','0.8',
        '0.2','0.2','0.2','0.5','0.2','0.7','0.5','1.1','0.6',
        '0.5','0.3','0.1','0.8','0.4','0.4','0.7','0.7','0.7',
        '0.1','0.4','0.3','0.6','0.3','0.6','0.4','0.7','0.6',
        '0','0','-0.2','0.3','0','0.3','0.3','0.6','0.4']
PANELS = ['p1']*9+['p2']*9+['p3']*9+['p4']*9+['p5']*9+['p6']*9
assert len(GOLD)==54

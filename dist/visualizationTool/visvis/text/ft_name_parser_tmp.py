
fname = 'c:/almar/projects/py/visvis/text/freetypewrapper.py'

text = open(fname, 'rt', encoding='utf-8').read()
exceptions = """ FT_Request_Size FT_GLYPH_FORMAT_OUTLINE 
    FT_LOAD_IGNORE_TRANSFORM FT_LOAD_LINEAR_DESIGN FT_LOAD_VERTICAL_LAYOUT
    FT_LOAD_XXX FT_PIXEL_MODE_GRAY FT_GLYPH_FORMAT_BITMAP FT_Load_Glyph
    FT_Pixel_Mode FT_Done_Glyph FT_SizeMetrics FT_Kerning_Mode 
    FT_Bitmap_Convert FT_GLYPH_FORMAT_COMPOSITE
    """

i = 0
words = set()
while True:
    
    # Find start of word
    i0 = text.find('FT_', i)
    if i0<0:
        break
    
    # Find end of word
    ii = [text.find(c, i0+1) for c in ' ,[]()\n.;']
    ii = [i for i in ii if i>0]
    i1 = min(ii)
    
    # Get word and prepare for next
    words.add(text[i0:i1])
    i = i1+1

# Split words
words1 = []
words2 = []
for word in words:
    if word in exceptions:
        pass
    elif word.upper() == word:
        words1.append(word)
    else:
        words2.append(word)
# Sort
words1.sort(key=lambda w:len(w))
words2.sort(key=lambda w:len(w))
# Print
print(', '.join(words1))
print()
print(', '.join(words2))

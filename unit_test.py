
img = create_texture(256)
draw_stroke(img, (0.1,0.1,0.5))
pretone = [ get_tone(img) ]

cv2.imwrite('pre.png', img)

copied = copy_imgs([img])
bad_stroke = (0.1,0.2,0.5)
bad = compute_goodness(copied, bad_stroke, pretone)
cv2.imwrite('bad.png', copied[0])

copied = copy_imgs([img])
good = compute_goodness(copied, (0.5,0.5,0.5), pretone)
cv2.imwrite('good.png', copied[0])

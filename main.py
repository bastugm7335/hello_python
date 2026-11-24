try:
    arial_font = pygame.font.match_font("arial")
    if arial_font:
        FONT = pygame.font.Font(arial_font, 24)
        SMALL_FONT = pygame.font.Font(arial_font, 18)
    else:
        FONT = pygame.font.Font(None, 24)
        SMALL_FONT = pygame.font.Font(None, 18)
except pygame.error:
    FONT = pygame.font.Font(None, 24)
    SMALL_FONT = pygame.font.Font(None, 18)

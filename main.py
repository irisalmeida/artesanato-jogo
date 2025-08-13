try:
    import pygbag.aio as asyncio
except ImportError:
    import asyncio

import pygame as pg
import random

WIDTH, HEIGHT = 900, 600
FPS = 60

pg.init()
screen = pg.display.set_mode((WIDTH, HEIGHT))
pg.display.set_caption("Jogo de Artesanato Terapêutico")
clock = pg.time.Clock()

FONT = pg.font.Font(None, 32)
BIG_FONT = pg.font.Font(None, 46)
SMALL_FONT = pg.font.Font(None, 24)

WHITE = (255, 255, 255)
BLACK = (20, 20, 20)
GOLD = (255, 215, 0)
BROWN = (139, 69, 19)
LIGHT_BROWN = (205, 133, 63)
BG_COLOR = (30, 30, 40)
SELECTED_COLOR = (100, 180, 100)

essencias = 0
etapa_atual = 0
escolhas = []
selecionadas = []

etapas = [
    {
        "titulo": "Tipos de Artesanato",
        "limite": 3,
        "opcoes": [
            ("Decoupage", 2, "Recorte figuras de revistas e crie um painel de paz."),
            ("Artesanato com EVA", 2, "Corte formas simples e monte um móbile colorido."),
            ("Biscuit", 3, "Modele pequenas flores para ímãs de geladeira."),
            ("Sabonete artesanal", 3, "Use base glicerinada e essência de lavanda."),
            ("Fuxico", 2, "Faça um fuxico com retalho e aplique em uma roupa."),
            ("Materiais reciclados", 3, "Transforme uma garrafa de vidro em vaso."),
            ("Cartonagem", 2, "Crie uma caixa para guardar memórias."),
            ("Sousplat e porta-copos", 2, "Faça um porta-copo com corda e cola."),
            ("Pintura em tecido", 4, "Pinte uma estampa simples em pano de prato."),
            ("Crochê", 3, "Aprenda ponto corrente e faça uma amostra."),
        ],
    },
    {
        "titulo": "Processos Criativos",
        "limite": 2,
        "opcoes": [
            ("Manualidade contemplativa", 2, "Trabalhe devagar, sentindo cada movimento."),
            ("Explosão artística", 3, "Use cores vibrantes para expressar emoções."),
            ("Planejamento funcional", 2, "Esboce no papel antes de começar."),
            ("Experimentação digital", 3, "Use aplicativos para testar combinações."),
            ("Criação intuitiva", 2, "Crie sem rascunho, deixando fluir."),
            ("Pesquisa simbólica", 2, "Pesquise símbolos que tragam significado."),
        ],
    },
    {
        "titulo": "Socialização",
        "limite": 3,
        "opcoes": [
            ("Compartilhar pesquisas", 2, "Mostre ideias para amigos."),
            ("Planejar com o coletivo", 3, "Junte-se a um grupo de artesãos."),
            ("Oficina interativa", 3, "Participe de um workshop local."),
            ("Exposição comunitária", 3, "Exponha seu trabalho em eventos."),
            ("Feira afetiva", 3, "Venda ou troque peças na feira."),
            ("Círculo de histórias", 2, "Conte a história da sua peça."),
        ],
    },
    {
        "titulo": "Empreendedorismo",
        "limite": 2,
        "opcoes": [
            ("Venda online", 3, "Crie uma página no Instagram."),
            ("Loja coletiva", 3, "Divida espaço em loja local."),
            ("Empreendedorismo social", 2, "Doe peças para causas."),
            ("Assinaturas artesanais", 3, "Ofereça kits mensais."),
            ("Eventos culturais", 3, "Venda em festas e feiras."),
        ],
    },
    {
        "titulo": "Dedicação",
        "limite": 3,
        "opcoes": [
            ("Inspiração inicial", 2, "Separe imagens e referências."),
            ("Execução técnica", 3, "Reserve 1h focada sem interrupções."),
            ("Ajustes e retoques", 2, "Revise detalhes após concluir."),
            ("Documentação do processo", 2, "Fotografe cada etapa."),
            ("Compartilhamento em rede", 2, "Publique fotos e receba feedback."),
        ],
    },
]

particles = []


def spawn_particles(x, y):
    for _ in range(10):
        particles.append([[x, y], [random.uniform(-1, 1), random.uniform(-2, -0.5)], random.randint(3, 6)])


def update_particles():
    for p in particles[:]:
        p[0][0] += p[1][0]
        p[0][1] += p[1][1]
        p[2] -= 0.1
        if p[2] <= 0:
            particles.remove(p)
        else:
            pg.draw.circle(screen, GOLD, (int(p[0][0]), int(p[0][1])), int(p[2]))


def draw_button(rect, text, selected):
    color = SELECTED_COLOR if selected else LIGHT_BROWN
    pg.draw.rect(screen, color, rect)
    pg.draw.rect(screen, BROWN, rect, 3)
    txt = FONT.render(text, True, WHITE)
    screen.blit(txt, (rect.x + (rect.width - txt.get_width()) // 2, rect.y + (rect.height - txt.get_height()) // 2))


def draw_final():
    screen.fill(BG_COLOR)
    pg.draw.rect(screen, LIGHT_BROWN, (60, 40, WIDTH - 120, HEIGHT - 80))
    pg.draw.rect(screen, BROWN, (60, 40, WIDTH - 120, HEIGHT - 80), 8)
    title = BIG_FONT.render("Dicas práticas:", True, BLACK)
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 60))
    y = 120
    for dim, nome, pts, dica in escolhas:
        line = SMALL_FONT.render(f"{dim}: {nome} (+{pts})", True, BLACK)
        screen.blit(line, (80, y))
        y += 22
        dica_line = SMALL_FONT.render(f"Dica: {dica}", True, BLACK)
        screen.blit(dica_line, (100, y))
        y += 28
    total = sum([pts for _, _, pts, _ in escolhas])
    screen.blit(SMALL_FONT.render(f"Total  Essências: {total}", True, BLACK), (80, y + 20))
    screen.blit(SMALL_FONT.render(f"Estresse: -{total*1}%", True, BLACK), (80, y + 50))
    screen.blit(SMALL_FONT.render(f"Depressão: -{round(total*0.8, 1)}%", True, BLACK), (80, y + 80))
    screen.blit(SMALL_FONT.render(f"Ansiedade: -{round(total*0.5, 1)}%", True, BLACK), (80, y + 110))


async def main():
    global etapa_atual, essencias
    running = True
    while running:
        dt = clock.tick(FPS) / 1000
        screen.fill(BG_COLOR)
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
            elif event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                if etapa_atual < len(etapas):
                    et = etapas[etapa_atual]
                    for i, (nome, pts, dica) in enumerate(et["opcoes"]):
                        rect = pg.Rect(150, 200 + i * 50, 600, 40)
                        if rect.collidepoint((mx, my)):
                            if nome in [n for _, n, _, _ in selecionadas]:
                                selecionadas.remove((et["titulo"], nome, pts, dica))
                            else:
                                if sum(1 for d, _, _, _ in selecionadas if d == et["titulo"]) < et["limite"]:
                                    selecionadas.append((et["titulo"], nome, pts, dica))
                                    spawn_particles(rect.centerx, rect.centery)
                    if sum(1 for d, _, _, _ in selecionadas if d == et["titulo"]) == et["limite"]:
                        for s in selecionadas:
                            if s not in escolhas:
                                escolhas.append(s)
                        etapa_atual += 1
                else:
                    etapa_atual = 0
                    escolhas.clear()
                    selecionadas.clear()
                    essencias = 0
        if etapa_atual < len(etapas):
            et = etapas[etapa_atual]
            title = BIG_FONT.render(et["titulo"], True, WHITE)
            screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 80))
            for i, (nome, pts, dica) in enumerate(et["opcoes"]):
                rect = pg.Rect(150, 200 + i * 50, 600, 40)
                sel = (et["titulo"], nome, pts, dica) in selecionadas
                draw_button(rect, f"{nome} (+{pts})", sel)
        else:
            draw_final()
        update_particles()
        pg.display.flip()
        await asyncio.sleep(0)


if __name__ == "__main__":
    asyncio.run(main())

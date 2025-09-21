try:
    import pygbag.aio as asyncio
except ImportError:
    import asyncio

import pygame as pg
import random
import math

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
RED = (200, 70, 70)
GREEN = (80, 170, 80)
BLUE = (70, 120, 200)
GRAY = (90, 90, 110)

essencias = 0
etapa_atual = 0
escolhas = []
selecionadas = []

FASE_ESCOLHAS = 0
FASE_SIMULACAO = 1
FASE_DICAS = 2
FASE_DIAGNOSTICO = 3
fase_jogo = FASE_ESCOLHAS

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


def draw_button(rect, text, selected=False):
    color = SELECTED_COLOR if selected else LIGHT_BROWN
    pg.draw.rect(screen, color, rect, border_radius=8)
    pg.draw.rect(screen, BROWN, rect, 3, border_radius=8)
    txt = FONT.render(text, True, WHITE)
    screen.blit(txt, (rect.x + (rect.width - txt.get_width()) // 2, rect.y + (rect.height - txt.get_height()) // 2))


def draw_simple_button(x, y, w, h, label):
    rect = pg.Rect(x, y, w, h)
    draw_button(rect, label, False)
    return rect


def draw_escolhas(et):
    title = BIG_FONT.render(et["titulo"], True, WHITE)
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 80))
    for i, (nome, pts, dica) in enumerate(et["opcoes"]):
        rect = pg.Rect(150, 200 + i * 50, 600, 40)
        sel = (et["titulo"], nome, pts, dica) in selecionadas
        draw_button(rect, f"{nome} (+{pts})", sel)


def draw_dicas():
    screen.fill(BG_COLOR)
    pg.draw.rect(screen, LIGHT_BROWN, (60, 40, WIDTH - 120, HEIGHT - 120), border_radius=12)
    pg.draw.rect(screen, BROWN, (60, 40, WIDTH - 120, HEIGHT - 120), 8, border_radius=12)
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
    screen.blit(SMALL_FONT.render(f"Total Essências: {total}", True, BLACK), (80, y + 20))
    screen.blit(SMALL_FONT.render(f"Estresse: -{total*1}%", True, BLACK), (80, y + 50))
    screen.blit(SMALL_FONT.render(f"Depressão: -{round(total*0.8, 1)}%", True, BLACK), (80, y + 80))
    screen.blit(SMALL_FONT.render(f"Ansiedade: -{round(total*0.5, 1)}%", True, BLACK), (80, y + 110))
    next_rect = draw_simple_button(WIDTH - 220, HEIGHT - 70, 160, 40, "Continuar ▶")
    return next_rect


def draw_diagnostico():
    screen.fill(BG_COLOR)
    pg.draw.rect(screen, LIGHT_BROWN, (60, 40, WIDTH - 120, HEIGHT - 80), border_radius=12)
    pg.draw.rect(screen, BROWN, (60, 40, WIDTH - 120, HEIGHT - 80), 8, border_radius=12)
    title = BIG_FONT.render("Perfil de Ansiedade (no jogo)", True, BLACK)
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 60))
    total = sum([pts for _, _, pts, _ in escolhas])
    if total >= 12:
        faixa = "Baixa"
        cor = GREEN
        texto = [
            "Você demonstrou boa regulação emocional durante o jogo.",
            "Siga praticando pausas conscientes e artesanato contemplativo.",
            "Mantenha rotinas que funcionam para você.",
        ]
    elif total >= 7:
        faixa = "Moderada"
        cor = BLUE
        texto = [
            "Alguns sinais de tensão apareceram, mas você encontrou saídas.",
            "Experimente agendar blocos curtos de artesanato (15–25 min).",
            "Teste técnicas de respiração e registro do processo.",
        ]
    else:
        faixa = "Elevada"
        cor = RED
        texto = [
            "O jogo sinalizou alta ativação ansiosa.",
            "Sugestão: microtarefas com passos muito simples e pausas frequentes.",
            "Se o incômodo persistir, considere conversar com um profissional.",
        ]
    badge = FONT.render(f"Classificação: {faixa}", True, WHITE)
    pg.draw.rect(screen, cor, (80, 120, badge.get_width() + 20, badge.get_height() + 14), border_radius=10)
    screen.blit(badge, (90, 127))
    y = 180
    for linha in texto:
        screen.blit(SMALL_FONT.render(linha, True, BLACK), (80, y))
        y += 28
    aviso = SMALL_FONT.render("Aviso: resultado lúdico, não é diagnóstico clínico.", True, BLACK)
    screen.blit(aviso, (80, y + 10))
    again = draw_simple_button(80, HEIGHT - 70, 200, 40, "Recomeçar")
    return again


SIM_AREA = pg.Rect(100, 120, 700, 360)
cut_progress = 0.0
cut_trace = []
cut_required = 100.0
glue_points = []
glue_hit = [False, False, False]
decor_targets = []
decor_shapes = []
sim_step = 0


def init_simulacao():
    global cut_progress, cut_trace, glue_points, glue_hit, decor_targets, decor_shapes, sim_step
    sim_step = 0
    cut_progress = 0.0
    cut_trace = []
    glue_points = [
        (SIM_AREA.centerx - 120, SIM_AREA.centery),
        (SIM_AREA.centerx, SIM_AREA.centery - 60),
        (SIM_AREA.centerx + 120, SIM_AREA.centery + 40),
    ]
    glue_hit = [False, False, False]
    decor_targets = [
        pg.Rect(SIM_AREA.left + 120, SIM_AREA.bottom - 120, 60, 60),
        pg.Rect(SIM_AREA.centerx - 30, SIM_AREA.bottom - 120, 60, 60),
        pg.Rect(SIM_AREA.right - 180, SIM_AREA.bottom - 120, 60, 60),
    ]
    decor_shapes = []
    base_y = SIM_AREA.bottom - 40
    for i in range(5):
        r = pg.Rect(SIM_AREA.left + 40 + i * 120, base_y, 40, 40)
        decor_shapes.append({"rect": r, "drag": False, "offset": (0, 0), "placed": False, "kind": i % 3})


def draw_progress_bar(x, y, w, h, value, max_value):
    pg.draw.rect(screen, GRAY, (x, y, w, h), border_radius=6)
    filled = int((value / max_value) * w)
    pg.draw.rect(screen, GREEN, (x, y, filled, h), border_radius=6)
    pg.draw.rect(screen, BLACK, (x, y, w, h), 2, border_radius=6)


def run_simulacao(events):
    global cut_progress, cut_trace, sim_step
    title = BIG_FONT.render("Simulação de Artesanato", True, WHITE)
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 60))
    pg.draw.rect(screen, LIGHT_BROWN, SIM_AREA, border_radius=10)
    pg.draw.rect(screen, BROWN, SIM_AREA, 4, border_radius=10)
    subtitulos = ["Etapa 1/3 — Cortar", "Etapa 2/3 — Colar", "Etapa 3/3 — Decorar"]
    if sim_step < 3:
        sub = FONT.render(subtitulos[sim_step], True, BLACK)
        screen.blit(sub, (SIM_AREA.left + 10, SIM_AREA.top + 10))
    if sim_step == 0:
        instr = SMALL_FONT.render("Arraste o mouse com o botão pressionado dentro da área para 'cortar'.", True, BLACK)
        screen.blit(instr, (SIM_AREA.left + 10, SIM_AREA.top + 40))
        mouse_pressed = pg.mouse.get_pressed()[0]
        mx, my = pg.mouse.get_pos()
        if mouse_pressed and SIM_AREA.collidepoint(mx, my):
            cut_trace.append((mx, my))
            cut_progress = min(cut_required, cut_progress + 0.6)
            if len(cut_trace) > 1:
                pg.draw.lines(screen, RED, False, cut_trace[-200:], 2)
        for i in range(6):
            x = SIM_AREA.left + 60 + i * 100
            pg.draw.line(screen, (230, 200, 180), (x, SIM_AREA.top + 80), (x, SIM_AREA.bottom - 100), 1)
        draw_progress_bar(SIM_AREA.left + 10, SIM_AREA.bottom - 40, SIM_AREA.width - 20, 20, cut_progress, cut_required)
        if cut_progress >= cut_required:
            sim_step = 1
    elif sim_step == 1:
        instr = SMALL_FONT.render("Clique nos 3 pontos de cola.", True, BLACK)
        screen.blit(instr, (SIM_AREA.left + 10, SIM_AREA.top + 40))
        for idx, (gx, gy) in enumerate(glue_points):
            color = GREEN if glue_hit[idx] else BLUE
            pg.draw.circle(screen, color, (gx, gy), 14)
            pg.draw.circle(screen, BLACK, (gx, gy), 14, 2)
        for event in events:
            if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                for idx, (gx, gy) in enumerate(glue_points):
                    if not glue_hit[idx]:
                        if math.hypot(mx - gx, my - gy) <= 16:
                            glue_hit[idx] = True
                            spawn_particles(gx, gy)
        if all(glue_hit):
            sim_step = 2
    elif sim_step == 2:
        instr = SMALL_FONT.render("Arraste 3 formas até os quadros-alvo.", True, BLACK)
        screen.blit(instr, (SIM_AREA.left + 10, SIM_AREA.top + 40))
        for t in decor_targets:
            pg.draw.rect(screen, (240, 230, 210), t, border_radius=6)
            pg.draw.rect(screen, BLACK, t, 2, border_radius=6)
        for event in events:
            if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                for s in decor_shapes:
                    if (not s["placed"]) and s["rect"].collidepoint(mx, my):
                        s["drag"] = True
                        s["offset"] = (mx - s["rect"].x, my - s["rect"].y)
            elif event.type == pg.MOUSEBUTTONUP and event.button == 1:
                for s in decor_shapes:
                    if s["drag"]:
                        s["drag"] = False
                        for t in decor_targets:
                            if t.colliderect(s["rect"]) and (not s["placed"]):
                                s["rect"].topleft = (t.x + 10, t.y + 10)
                                s["placed"] = True
                                spawn_particles(s["rect"].centerx, s["rect"].centery)
                                break
        if pg.mouse.get_pressed()[0]:
            mx, my = pg.mouse.get_pos()
            for s in decor_shapes:
                if s["drag"]:
                    s["rect"].x = mx - s["offset"][0]
                    s["rect"].y = my - s["offset"][1]
        for s in decor_shapes:
            color = (200, 120, 80) if s["kind"] == 0 else (120, 200, 160) if s["kind"] == 1 else (180, 120, 200)
            pg.draw.rect(screen, color, s["rect"], border_radius=6)
            pg.draw.rect(screen, BLACK, s["rect"], 2, border_radius=6)
        placed_count = sum(1 for s in decor_shapes if s["placed"])
        if placed_count >= 3:
            sim_step = 3
    if sim_step == 3:
        done_msg = FONT.render("Simulação concluída!", True, WHITE)
        screen.blit(done_msg, (SIM_AREA.centerx - done_msg.get_width() // 2, SIM_AREA.top + 70))
        cont_rect = draw_simple_button(WIDTH - 220, HEIGHT - 70, 160, 40, "Ir às Dicas ▶")
        return cont_rect
    return None


async def main():
    global etapa_atual, essencias, fase_jogo, selecionadas, escolhas
    running = True
    while running:
        dt = clock.tick(FPS) / 1000
        screen.fill(BG_COLOR)
        events = pg.event.get()
        for event in events:
            if event.type == pg.QUIT:
                running = False
            if fase_jogo == FASE_ESCOLHAS:
                if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                    mx, my = event.pos
                    if etapa_atual < len(etapas):
                        et = etapas[etapa_atual]
                        for i, (nome, pts, dica) in enumerate(et["opcoes"]):
                            rect = pg.Rect(150, 200 + i * 50, 600, 40)
                            if rect.collidepoint((mx, my)):
                                if (et["titulo"], nome, pts, dica) in selecionadas:
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
                            selecionadas = [s for s in selecionadas if s[0] != et["titulo"]]
                        if etapa_atual >= len(etapas):
                            fase_jogo = FASE_SIMULACAO
                            init_simulacao()
            elif fase_jogo == FASE_SIMULACAO:
                pass
            elif fase_jogo == FASE_DICAS:
                if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                    mx, my = event.pos
                    pass
            elif fase_jogo == FASE_DIAGNOSTICO:
                if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                    mx, my = event.pos
                    pass
        if fase_jogo == FASE_ESCOLHAS:
            if etapa_atual < len(etapas):
                draw_escolhas(etapas[etapa_atual])
        elif fase_jogo == FASE_SIMULACAO:
            cont_rect = run_simulacao(events)
            if cont_rect:
                for event in events:
                    if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                        if cont_rect.collidepoint(event.pos):
                            fase_jogo = FASE_DICAS
        elif fase_jogo == FASE_DICAS:
            next_rect = draw_dicas()
            for event in events:
                if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                    if next_rect.collidepoint(event.pos):
                        fase_jogo = FASE_DIAGNOSTICO
        elif fase_jogo == FASE_DIAGNOSTICO:
            again_rect = draw_diagnostico()
            for event in events:
                if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                    if again_rect.collidepoint(event.pos):
                        etapa_atual = 0
                        escolhas.clear()
                        selecionadas.clear()
                        fase_jogo = FASE_ESCOLHAS
        update_particles()
        pg.display.flip()
        await asyncio.sleep(0)


if __name__ == "__main__":
    asyncio.run(main())

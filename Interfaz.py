import pygame
import joblib
import os
import pandas as pd
from Astronauta import Astronauta

pygame.init()

height = 900
width = 1200

window = pygame.display.set_mode((width, height))
pygame.display.set_caption("Will you be transported?")

background = pygame.image.load("space.jpg").convert()

# Se escala el fondo para que esté en las dimensiones de la ventana
scaled_background = pygame.transform.scale(background, (width, height))


# Imagen del astronauta
astronauta = Astronauta(650, 700, 200, 200)


# Colores que quizá use
NEGRO_ESPACIO = (10, 10, 18)
AZUL_ABISMO   = (15, 23, 42)
PURPURA_NEB   = (48, 25, 52)

BLANCO_ESTRELLA = (240, 246, 252)

# Neones
CIAN_NEON     = (0, 245, 212)
MAGENTA_LASER = (247, 37, 133)
VERDE_ALIEN   = (57, 255, 20)
NARANJA_FUEGO = (255, 107, 0)
AMARILLO_SOL  = (255, 214, 10)
GRIS_DESHABILITADO = (110, 116, 130)

# Fonts 
font = pygame.font.Font("PressStart2P-Regular.ttf", 16)
font2 = pygame.font.SysFont("couriernew", 24, bold=True)

state_text = ""

def draw_state_text(surface):
    if state_text != "":
        text_surface = font2.render(state_text, True, BLANCO_ESTRELLA)
        text_rect = text_surface.get_rect(center=(950, 750))
        surface.blit(text_surface, text_rect)


# Se colocan los modelos

models = {
    "Logistic Regression": "modelos/logistic_regression.pkl",
    "Random Forest": "modelos/random_forest.pkl",
    "Decision Tree": "modelos/decision_tree.pkl",
    "SVM": "modelos/svm.pkl",
    "Neural Network": "modelos/neural_network.pkl"
}


# Aquí se va a guardar el modelo que se selecciones 
selected_model = None  


# ---------------------------------------------------------------------------
# Artefactos de preprocesamiento que se iban generando en cada notebook, esto para que esté escalado igual 
# Estos dos se obtuvieron del notebook de preprocesamiento  
#   - robust_scaler.pkl: RobustScaler ajustado sobre [Age, RoomService, FoodCourt, ShoppingMall, Spa, VRDeck]
#   - feature_columns.pkl: lista de columnas de X en el orden exacto que espera el modelo (salida de pd.get_dummies)
#   - standard_scaler.pkl: StandardScaler que se usan en el entrenamiento (solo lo usan Logistic Regression y SVM)
# ---------------------------------------------------------------------------
ARTIFACTS_DIR = "modelos"
NUM_COLS = ["Age", "RoomService", "FoodCourt", "ShoppingMall", "Spa", "VRDeck"]
MODELS_SCALER = {"Logistic Regression", "SVM", "Neural Network"}

robust_scaler = None
standard_scaler = None
feature_columns = None


def _cargar_artefactos():
    global robust_scaler, standard_scaler, feature_columns
    try:
        robust_scaler = joblib.load(os.path.join(ARTIFACTS_DIR, "robust_scaler.pkl"))
        feature_columns = joblib.load(os.path.join(ARTIFACTS_DIR, "feature_columns.pkl"))
    except FileNotFoundError:
        print("nO ESTÁ robust_scaler.pkl o feature_columns.pkl en", ARTIFACTS_DIR)
    try:
        standard_scaler = joblib.load(os.path.join(ARTIFACTS_DIR, "standard_scaler.pkl"))
    except FileNotFoundError:
        print("No está standard_scaler.pkl en", ARTIFACTS_DIR)


_cargar_artefactos()


# sE inicializan los botones para seleccionar el modelo. 


model_buttons = []


class ModelButton:
    def __init__(self, x, y, w, h, text, model_path):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text                # Este es el nombre del modelo
        self.model_path = model_path    # pATh del modelo
        self.color = GRIS_DESHABILITADO

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)
        text_surface = font.render(self.text, True, BLANCO_ESTRELLA)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

    def handle_event(self, event):
        global selected_model
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                selected_model = self.text  # Se guarda el modelo que se selecciona
                # Cambiar el color del botón seleccionado
                for button in model_buttons: # Para cambiar el color del modeo seleccionado u que los demás se pongan gris
                    button.color = GRIS_DESHABILITADO
                self.color = CIAN_NEON


# Botones para los modelos
x = 100
y = 550
button_width = 350
button_height = 50

for model_name, model_path in models.items():
    button = ModelButton(
        x,
        y,
        button_width,
        button_height,
        model_name,
        model_path
    )

    model_buttons.append(button)

    y += 60


class Checkbox:
    # Clase para crear un checkbox que puede ser marcado o desmarcado, puede haber de grupos para que solo se seleccione y se desmarque uno de ellos.   

    def __init__(self, x, y, size, label, group=None):
        self.rect = pygame.Rect(x, y, size, size)
        self.label = label
        self.checked = False
        self.group = group          # lista compartida entre los checkboxes de la misma categoría
        if self.group is not None:
            self.group.append(self)

        self.text_surface = font.render(self.label, True, BLANCO_ESTRELLA)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                if self.checked:
                    # Permite desmarcar haciendo clic de nuevo
                    self.checked = False
                else:
                    self.checked = True
                    # Desmarca a los demás miembros de la misma categoría
                    if self.group is not None:
                        for other in self.group:
                            if other is not self:
                                other.checked = False

    def draw(self, surface):
        pygame.draw.rect(surface, BLANCO_ESTRELLA, self.rect, 2)
        if self.checked:
            pygame.draw.line(surface, CIAN_NEON,
                              (self.rect.left + 5, self.rect.centery),
                              (self.rect.centerx, self.rect.bottom - 5), 2)
            pygame.draw.line(surface, CIAN_NEON,
                              (self.rect.centerx, self.rect.bottom - 5),
                              (self.rect.right - 5, self.rect.top + 5), 2)
        surface.blit(self.text_surface, (self.rect.right + 10, self.rect.top))


class InputBox:

    def __init__(self, x, y, w, h, label="", default_text=""):
        self.rect = pygame.Rect(x, y, w, h)
        self.label = label
        self.text = str(default_text)
        self.value = int(default_text) if default_text != "" else 0
        self.color = BLANCO_ESTRELLA
        self.active = False

        self.label_surface = font.render(self.label, True, BLANCO_ESTRELLA)
        self.txt_surface = font.render(self.text, True, self.color)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
            self.color = CIAN_NEON if self.active else BLANCO_ESTRELLA
            self.txt_surface = font.render(self.text, True, self.color)

        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_RETURN:
                self.active = False
                self.color = BLANCO_ESTRELLA
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            else:
                if event.unicode.isdigit():
                    self.text += event.unicode

            self.txt_surface = font.render(self.text, True, self.color)
            self.value = int(self.text) if self.text != "" else 0

    def draw(self, surface):
        surface.blit(self.label_surface, (self.rect.x, self.rect.y - 22))
        pygame.draw.rect(surface, self.color, self.rect, 2)
        surface.blit(self.txt_surface, (self.rect.x + 8, self.rect.y + 5))


class ReadOnlyBox:
    # Esta es para mostrar os valores de lectura que son el total que se gastó.

    def __init__(self, x, y, w, h, label="", value=""):
        self.rect = pygame.Rect(x, y, w, h)
        self.label = label
        self.label_surface = font.render(self.label, True, BLANCO_ESTRELLA)
        self.set_value(value)

    def set_value(self, value):
        self.text = str(value)
        self.txt_surface = font.render(self.text, True, GRIS_DESHABILITADO)

    def draw(self, surface):
        surface.blit(self.label_surface, (self.rect.x, self.rect.y - 22))
        pygame.draw.rect(surface, GRIS_DESHABILITADO, self.rect, 2)
        surface.blit(self.txt_surface, (self.rect.x + 8, self.rect.y + 5))


class ReadOnlyCheckbox:
    # Esta es para mostrar el indicador de si gastó algo o no, que es un checkbox de solo lectura.

    def __init__(self, x, y, size, label):
        self.rect = pygame.Rect(x, y, size, size)
        self.label = label
        self.checked = False
        self.text_surface = font.render(self.label, True, BLANCO_ESTRELLA)

    def set_checked(self, checked):
        self.checked = checked

    def draw(self, surface):
        pygame.draw.rect(surface, GRIS_DESHABILITADO, self.rect, 2)
        if self.checked:
            pygame.draw.line(surface, VERDE_ALIEN,
                              (self.rect.left + 5, self.rect.centery),
                              (self.rect.centerx, self.rect.bottom - 5), 2)
            pygame.draw.line(surface, VERDE_ALIEN,
                              (self.rect.centerx, self.rect.bottom - 5),
                              (self.rect.right - 5, self.rect.top + 5), 2)
        surface.blit(self.text_surface, (self.rect.right + 10, self.rect.top))


class Button:
    # La clase para crear un botón que ejecuta una función al hacer clic.

    def __init__(self, x, y, w, h, label, on_click):
        self.rect = pygame.Rect(x, y, w, h)
        self.label = label
        self.on_click = on_click
        self.text_surface = font.render(self.label, True, NEGRO_ESPACIO)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.on_click()

    def draw(self, surface):
        pygame.draw.rect(surface, AMARILLO_SOL, self.rect)
        pygame.draw.rect(surface, BLANCO_ESTRELLA, self.rect, 2)
        text_rect = self.text_surface.get_rect(center=self.rect.center)
        surface.blit(self.text_surface, text_rect)


# Las listas de checkboxes para las categorías mutuamente excluyentes
home_planet_group = []
destination_group = []
deck_group = []
side_group = []

# Para los datos de checkbox que no estan en grupos (Cryosleep y VIP)
cryosleep = Checkbox(50, 50, 20, "Cryosleep")
vip = Checkbox(50, 90, 20, "VIP")
# Iput boxes para los datos de edad y número de cabina
input_box1 = InputBox(310, 50, 140, 32, "Age", "0")
cabin_num_box = InputBox(310, 110, 140, 32, "Cabin Number", "0")

# HomePlanet (mutuamente excluyentes)
home_planet_earth = Checkbox(50, 190, 20, "HomePlanet: Earth", group=home_planet_group)
home_planet_europa = Checkbox(50, 220, 20, "HomePlanet: Europa", group=home_planet_group)
home_planet_mars = Checkbox(50, 250, 20, "HomePlanet: Mars", group=home_planet_group)

# Destination (mutuamente excluyentes) 
trappist_1e = Checkbox(50, 300, 20, "Destination: TRAPPIST-1e", group=destination_group)
cancri_e = Checkbox(50, 330, 20, "Destination: 55 Cancri e", group=destination_group)
pso_j318_5_22 = Checkbox(50, 360, 20, "Destination: PSO J318.5-22", group=destination_group)

# Deck (mutuamente excluyentes) 
deck_a = Checkbox(520, 50, 20, "Deck A", group=deck_group)
deck_b = Checkbox(520, 80, 20, "Deck B", group=deck_group)
deck_c = Checkbox(520, 110, 20, "Deck C", group=deck_group)
deck_d = Checkbox(520, 140, 20, "Deck D", group=deck_group)
deck_e = Checkbox(520, 170, 20, "Deck E", group=deck_group)
deck_f = Checkbox(520, 200, 20, "Deck F", group=deck_group)
deck_g = Checkbox(520, 230, 20, "Deck G", group=deck_group)
deck_t = Checkbox(520, 260, 20, "Deck T", group=deck_group)

# Side (mutuamente excluyentes)
side_s = Checkbox(520, 300, 20, "Side S", group=side_group)
side_p = Checkbox(520, 330, 20, "Side P", group=side_group)

# Se puede editar los gastos de cada servicio, que son los que se van a escalar y sumar para el total.
expenses_room_service = InputBox(800, 60, 140, 32, "Room Service", "0")
expenses_food_court = InputBox(800, 130, 140, 32, "FoodCourt", "0")
expenses_shopping_mall = InputBox(800, 200, 140, 32, "ShoppingMall", "0")
expenses_spa = InputBox(800, 270, 140, 32, "Spa", "0")
expenses_VRDeck = InputBox(800, 340, 140, 32, "VRDeck", "0")

expense_boxes = [
    expenses_room_service,
    expenses_food_court,
    expenses_shopping_mall,
    expenses_spa,
    expenses_VRDeck,
]

# Campo de solo lectura para mostrar el total gastado y si tiene gastos o no.
total_spent_box = ReadOnlyBox(800, 420, 140, 32, "Total Spent", "0")
has_expenses_box = ReadOnlyCheckbox(800, 480, 20, "Has Expenses")

# Aquí se va a mostrar el resultado de la predicción, que es un campo de solo lectura.
prediction_box = ReadOnlyBox(100, 480, 350, 32, "Prediction", "-")


# pARA ver que se selecciona
def group_value(group, value_map):
    for checkbox in group:
        if checkbox.checked:
            return value_map[checkbox]
    return None  


def build_feature_row():
    # Aquí se hace la construcción de la fila de características a partir de los inputs del usuario, incluyendo el escalado y las dummies, para que se parezca a 
    # lo del notebook, y que los modelos puedan hacer las predicciones.
    
    if robust_scaler is None or feature_columns is None:
        return None

    home_planet = group_value(home_planet_group, {
        home_planet_earth: "Earth",
        home_planet_europa: "Europa",
        home_planet_mars: "Mars",
    })
    destination = group_value(destination_group, {
        trappist_1e: "TRAPPIST-1e",
        cancri_e: "55 Cancri e",
        pso_j318_5_22: "PSO J318.5-22",
    })
    deck = group_value(deck_group, {
        deck_a: "A", deck_b: "B", deck_c: "C", deck_d: "D",
        deck_e: "E", deck_f: "F", deck_g: "G", deck_t: "T",
    })
    side = group_value(side_group, {side_s: "S", side_p: "P"})

    # Se escalan los valores de edad y gastos usando el robust_scaler que se cargó desde el .pkl
    valores_crudos = [[
        input_box1.value,
        expenses_room_service.value,
        expenses_food_court.value,
        expenses_shopping_mall.value,
        expenses_spa.value,
        expenses_VRDeck.value,
    ]]
    age_s, room_s, food_s, shop_s, spa_s, vr_s = robust_scaler.transform(valores_crudos)[0]
    total_spent = room_s + food_s + shop_s + spa_s + vr_s
    has_expenses = 1 if total_spent > 0 else 0

    # Se construye un diccionario con todas las columnas de características, inicializadas en 0, y luego se llenan con los valores del usuario.
    row = {col: 0 for col in feature_columns}

    if "Age" in row:
        row["Age"] = age_s
    if "RoomService" in row:
        row["RoomService"] = room_s
    if "FoodCourt" in row:
        row["FoodCourt"] = food_s
    if "ShoppingMall" in row:
        row["ShoppingMall"] = shop_s
    if "Spa" in row:
        row["Spa"] = spa_s
    if "VRDeck" in row:
        row["VRDeck"] = vr_s
    if "Total_Spent" in row:
        row["Total_Spent"] = total_spent
    if "Has_Expenses" in row:
        row["Has_Expenses"] = has_expenses
    if "CryoSleep" in row:
        row["CryoSleep"] = int(cryosleep.checked)
    if "VIP" in row:
        row["VIP"] = int(vip.checked)
    if "CabinNum" in row:
        row["CabinNum"] = cabin_num_box.value

    seleccion_por_prefijo = {
        "HomePlanet_": home_planet,
        "Destination_": destination,
        "Deck_": deck,
        "Side_": side,
    }
    for col in feature_columns:
        for prefijo, valor in seleccion_por_prefijo.items():
            if col.startswith(prefijo) and valor is not None and col == f"{prefijo}{valor}":
                row[col] = 1

    return pd.DataFrame([row])[feature_columns]  # fuerza el orden exacto


def run_prediction():
    global state_text
    if selected_model is None:
        prediction_box.set_value("Elige un modelo")
        return

    if robust_scaler is None or feature_columns is None:
        prediction_box.set_value("Faltan artefactos .pkl")
        return

    model_path = models[selected_model]
    if not os.path.exists(model_path):
        prediction_box.set_value(f"No existe: {model_path}")
        return

    try:
        model = joblib.load(model_path)
        X = build_feature_row()

        if selected_model in MODELS_SCALER:
            if standard_scaler is None:
                prediction_box.set_value("Falta standard_scaler.pkl")
                return
            X_final = standard_scaler.transform(X.values)
        else:
            X_final = X.values

        # Validación temprana: evita el traceback críptico de sklearn si algún
        # .pkl quedó desfasado (entrenado con otra cantidad de columnas).
        n_esperadas = getattr(model, "n_features_in_", None)
        if n_esperadas is not None and n_esperadas != X_final.shape[1]:
            prediction_box.set_value(
                f"Desfase: modelo espera {n_esperadas}, hay {X_final.shape[1]}"
            )
            print(f"[Aviso] {selected_model} espera {n_esperadas} features, "
                  f"pero se construyeron {X_final.shape[1]}.")
            return

        pred = model.predict(X_final)[0]

        # Se cambia elestado del astronauta según la predicción
        if bool(pred):

            astronauta.cambiar_estado("transportado")
            state_text = "YOU WERE TRANSPORTED!!"

        else:
            astronauta.cambiar_estado("no_transportado")
            state_text = "YOU ARE SAFE!!"


       
        # Se muestra la probabilidad del modelo si tiene el método predict_proba (como regresión logística, random forest, etc.)
        if hasattr(model, "predict_proba"):
            proba = model.predict_proba(X_final)[0]
            confianza = max(proba) * 100
            prediction_box.set_value(f"{bool(pred)} ({confianza:.1f}%)")
        else:
            prediction_box.set_value(str(bool(pred)))
    except Exception as e:
        # Errores
        print("Error al predecir:", e)
        prediction_box.set_value("Error (ver consola)")


predict_button = Button(500, 450, 200, 45, "PREDICT", run_prediction)

# Todos los widgets que reciben eventos de mouse/teclado
interactive_widgets = [
    cryosleep, vip, input_box1, cabin_num_box,
    home_planet_earth, home_planet_europa, home_planet_mars,
    trappist_1e, cancri_e, pso_j318_5_22,
    deck_a, deck_b, deck_c, deck_d, deck_e, deck_f, deck_g, deck_t,
    side_s, side_p,
    expenses_room_service, expenses_food_court, expenses_shopping_mall,
    expenses_spa, expenses_VRDeck,
    predict_button,
]

# Todo lo que se dibuja 
drawable_widgets = interactive_widgets + [total_spent_box, has_expenses_box, prediction_box]

reloj = pygame.time.Clock()
ejecutando = True

while ejecutando:

    dt = reloj.tick(60) / 1000

    for evento in pygame.event.get():

        if evento.type == pygame.QUIT:
            ejecutando = False

        for widget in interactive_widgets:
            widget.handle_event(evento)


        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:

            if cryosleep.rect.collidepoint(evento.pos):

                if cryosleep.checked:
                    astronauta.cambiar_estado("dormido")
                else:
                    astronauta.cambiar_estado("normal")


        for button in model_buttons:
            button.handle_event(evento)


    # Los campos de gastos se suman para calcular el total gastado y si tiene gastos o no, y se actualizan los campos de solo lectura.

    total_spent = sum(box.value for box in expense_boxes)

    total_spent_box.set_value(total_spent)

    has_expenses_box.set_checked(total_spent > 0)


    # Se actualiza la imagen del astronauta según el estado y el tiempo transcurrido
    astronauta.actualizar( dt, not cryosleep.checked)

    window.blit(scaled_background, (0, 0))

    for widget in drawable_widgets:
        widget.draw(window)

    for button in model_buttons:
        button.draw(window)

    astronauta.draw(window)
    draw_state_text(window)


    pygame.display.flip()


pygame.quit()
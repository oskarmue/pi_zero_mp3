import math
import matplotlib.pyplot as plt

def backward_punkte_berechnen(resolution, widgetbreite, db_halbe, dh):
    #resolution = 16
    step_in_percent = 1/resolution
    step_in_pixel = 1/resolution * widgetbreite #bildbreite = 200
    widgetbreite_halbiert = round(widgetbreite/2)

    # Vertices
    vertices = []
    for i in range(resolution+1):
        for j in range(resolution+1):
            vertices += [
                round(j*step_in_pixel),
                round(i*step_in_pixel),
                round(j*step_in_percent, 2),
                round(i*step_in_percent, 2)
            ]

    # Indices
    indices = []
    for i in range(resolution):
        for j in range(resolution):
            bl = i*(resolution+1) + j
            br = bl + 1
            tl = bl + (resolution+1)
            tr = tl + 1
            indices += [bl, br, tr, bl, tr, tl]

    #calculating the vertices after the perspective change

    #1. verschiebung der Punkte in der obersten reihe berechnen

    #2. Winkel der vertikalen berechnen

    #3. Die Zeilen entlang die punte neu berechnen
        #3.1 horizontale stauchung mittels winkel tan(winkel) * 

        #3.2 vertikale stauchung gleichmäßig -> gesamtstauchung/anzahl punkte = dh

    #NACH VORNE KIPPEN -> OBEREN PUNKTE VERÄNDERN
    #winkel_berechnen



    nur_x_y_vor = []
    for i in range(0, len(vertices), 4):
        if i + 1 < len(vertices):
            nur_x_y_vor.append(vertices[i])
            nur_x_y_vor.append(vertices[i+1])


    obere_punkte = nur_x_y_vor[-1*(resolution+1)*2:]
    untere_punkte = nur_x_y_vor[:(resolution+1)*2]


    #1. verschiebung der Punkte in der obersten Reihe berechnen
    #reduktion der y werte
    obere_punkte[1::2] = [x - dh for x in obere_punkte[1::2]]
    #reduktion der x werte
    stauchungsfaktor = db_halbe/widgetbreite_halbiert
    for i in range(len(obere_punkte)):
        if i%2 == 0: #das sind die x werte
            if obere_punkte[i] < widgetbreite_halbiert:#dann sind wir links der mitte und die verschiebung wird auf den Punkt addiert
                verschiebung = stauchungsfaktor * (widgetbreite_halbiert - obere_punkte[i])
                obere_punkte[i] = obere_punkte[i] + verschiebung
            else: #wir sind rechts der mitte und die Verschiebung wird von dem Punkt subtrahiert
                verschiebung = stauchungsfaktor * (obere_punkte[i]-widgetbreite_halbiert)
                obere_punkte[i] = obere_punkte[i] - verschiebung
            
    #2. winkel der vertikalen berechnen
    winkel = []
    for i in range(0, (resolution+1)*2, 2):
        dx = obere_punkte[i] - untere_punkte[i]
        dy = untere_punkte[i+1] - obere_punkte[i+1]
        winkel.append(math.atan(dx/dy)) #in radians - positiv mit der rechten daumen regel

    #3. Die Zeilen entlang die punte neu berechnen
        #3.1 horizontale stauchung mittels winkel tan(winkel) * 

        #3.2 vertikale stauchung gleichmäßig -> gesamtstauchung/anzahl zeilen = dh
    vertices_nach_wechsel = vertices[:(resolution+1)*4]

    for i in range(1, resolution+1): #vertikal - da wir untere und obere reihe schon haben, können wir diese einfach einfügen
        for j in range(resolution + 1):

                x_koor = round(j*step_in_pixel)
                y_koor = round(i*step_in_pixel)
                x_verh = round(j*step_in_percent, 2)
                y_verh = round(i*step_in_percent, 2)

                y_koor = y_koor - round(dh * y_verh, 2)

                if x_koor < widgetbreite_halbiert:#dann sind wir links der mitte und die verschiebung wird auf den Punkt addiert
                    verschiebung = math.tan(winkel[j]) * y_koor 
                    x_koor = x_koor - verschiebung
                else: #wir sind rechts der mitte und die Verschiebung wird von dem Punkt subtrahiert
                    verschiebung = math.tan(winkel[j]) * y_koor 
                    x_koor = x_koor - verschiebung

                vertices_nach_wechsel += [
                    x_koor,
                    y_koor,
                    x_verh, #bleibt gleich
                    y_verh  #bleibt gleich
                ]

    #vertices_nach_wechsel = vertices_nach_wechsel + vertices[-(resolution+1)*4:]


    return indices, vertices, vertices_nach_wechsel

def forward_punkte_berechnen(resolution, widgetbreite, db_halbe, dh):

    step_in_percent = 1 / resolution
    step_in_pixel = widgetbreite / resolution
    widgetbreite_halbiert = widgetbreite / 2

    # --- Ursprüngliche Vertices ---
    vertices = []
    for i in range(resolution + 1):
        for j in range(resolution + 1):
            vertices += [
                round(j * step_in_pixel),
                round(i * step_in_pixel),
                round(j * step_in_percent, 2),
                round(i * step_in_percent, 2)
            ]

    # --- Indices ---
    indices = []
    for i in range(resolution):
        for j in range(resolution):
            bl = i * (resolution + 1) + j
            br = bl + 1
            tl = bl + (resolution + 1)
            tr = tl + 1
            indices += [bl, br, tr, bl, tr, tl]

    # --- obere & untere Punkte extrahieren ---
    nur_x_y = []
    for i in range(0, len(vertices), 4):
        nur_x_y.append(vertices[i])
        nur_x_y.append(vertices[i + 1])

    obere_punkte = nur_x_y[-(resolution + 1) * 2:]     # bleiben gleich
    untere_punkte = nur_x_y[:(resolution + 1) * 2]     # werden verändert

    # --- 1. Untere Punkte vertikal nach oben ziehen ---
    untere_punkte[1::2] = [y + dh for y in untere_punkte[1::2]]

    # --- 2. Horizontale Stauchung der unteren Punkte ---
    stauchungsfaktor = db_halbe / widgetbreite_halbiert

    for i in range(0, len(untere_punkte), 2):
        x = untere_punkte[i]
        if x < widgetbreite_halbiert:
            verschiebung = stauchungsfaktor * (widgetbreite_halbiert - x)
            untere_punkte[i] = x - verschiebung
        else:
            verschiebung = stauchungsfaktor * (x - widgetbreite_halbiert)
            untere_punkte[i] = x - verschiebung

    # --- 3. Winkel von oben nach unten ---
    winkel = []
    for i in range(0, (resolution + 1) * 2, 2):
        dx = untere_punkte[i] - obere_punkte[i]
        dy = untere_punkte[i + 1] - obere_punkte[i + 1]
        winkel.append(math.atan(dx / dy))

    # --- 4. Neue Vertices berechnen ---
    vertices_nach_wechsel = []

    for i in range(resolution + 1):
        y_verh = i * step_in_percent
        y_koor = i * step_in_pixel

        # vertikale Bewegung nimmt nach unten zu
        y_koor += dh * (1 - y_verh)

        for j in range(resolution + 1):
            x_koor = j * step_in_pixel
            x_verh = j * step_in_percent

            # horizontale Stauchung nimmt nach unten zu
            verschiebung = math.tan(winkel[j]) * (1 - y_verh) * step_in_pixel * resolution

            if x_koor < widgetbreite_halbiert:
                x_koor += verschiebung
            else:
                x_koor -= verschiebung

            vertices_nach_wechsel += [
                round(x_koor, 2),
                round(y_koor, 2),
                round(x_verh, 2),
                round(y_verh, 2)
            ]

    return indices, vertices, vertices_nach_wechsel

def plot_vertices(vertice_1, vertice_2):
    # x/y aus vertice_1 extrahieren
    x1 = vertice_1[0::4]
    y1 = vertice_1[1::4]

    # x/y aus vertice_2 extrahieren
    x2 = vertice_2[0::4]
    y2 = vertice_2[1::4]

    plt.figure(figsize=(6, 6))
    plt.scatter(x1, y1, color='red', label='Vertices 1', s=20)
    plt.scatter(x2, y2, color='blue', label='Vertices 2', s=20)

    plt.xlabel('x')
    plt.ylabel('y')
    plt.axis('equal')
    plt.legend()
    plt.grid(True)

    plt.show()

indices_b, vertices_b, vertices_nach_wechsel_b = backward_punkte_berechnen(1, 200, 20, 20)
indices_f, vertices_f, vertices_nach_wechsel_f = forward_punkte_berechnen(4, 200, 20, 20)

plot_vertices(vertices_f, vertices_nach_wechsel_f)
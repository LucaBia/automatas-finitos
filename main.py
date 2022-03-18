#  Gian Luca Rivera - 18049

from binarytree import Node
import graphviz

class Arbol:
    def __init__(self, valor, izquierda = None, derecha = None):
        self.valor = valor
        self.izquierda = izquierda
        self.derecha = derecha

# r = input("Ingrese r: ")
# r = "abb"
# r = "a*"
# r = "a|b"
# r = "(a|b)*abb"
r = "(b|b)*abb(a|b)*"

# w = input("Ingrese w: ")
w = "babbaaaaa"


padre_actual = None # instancia cabeza actual
arboles_temporales = [] # arboles temporales / hijos

alfabeto = "abcdefghijklmnopqrstuvwxyz"
operadores ="*+?"
# alfabeto = 0-25 ; operadores= 26(*), 27(+), 28(?) ; 29(.) ; 30(|)
caracteres = alfabeto + operadores + "." + "|"
SUB = str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")



# Valida si el nodo se agrega al arbol principal o a un arbol temporal
def nuevo_nodo(indice, valor, izquierda, derecha, padre_actual):
    if indice is None:
        if padre_actual is None:
            # Es la cabeza 
            padre_actual = Arbol(valor, izquierda, derecha)
        else:
            # Si hay cabeza el elemento actual hace todos los nodos pasado el hijo (derecho) de este
            padre_actual = Arbol(valor, padre_actual, derecha)
    # Arbol temporal
    else:
        # Si se debe crear un arbol temporal
        if indice == len(arboles_temporales):
            arboles_temporales.append(Arbol(valor, izquierda, derecha))
        # Si el nodo se debe agregar a un arbol temporal existente, misma logica pasada
        elif indice < len(arboles_temporales):
            if arboles_temporales[indice] is None:
                arboles_temporales[indice] = Arbol(valor, izquierda, derecha)
            else:
                arboles_temporales[indice] = Arbol(valor, arboles_temporales[indice], derecha)
    return padre_actual


# Cuenta la cantidad de parentesis abiertos y cerrados
# Analiza cuando termina una expresión 
# (c|(d|(e|f)))*abc
# (c|(d|(e|f)))*
# (d|(e|f))
# (e|f)
# abc
def expresiones_en_r(expresion_regular):
    long_exp = len(expresion_regular)
    i = 0
    while i < long_exp:
        if expresion_regular[i] == "(":
            cont_parentesis = 1
            for j in range(i+1, long_exp):
                if expresion_regular[j] == "(":
                    cont_parentesis += 1
                elif expresion_regular[j] == ")":
                    cont_parentesis -= 1

                contador = 0
                if cont_parentesis == 0 and expresion_regular[j] == ")":
                    if j + 1 < long_exp:
                        if expresion_regular[j+1] in operadores:
                            contador += 2

                    return contador + j

        elif expresion_regular[i] in alfabeto or expresion_regular[i] == "*":
            fin_exp = i
            for j in range(i+1, long_exp):
                if not (expresion_regular[j] in alfabeto or expresion_regular[j] == "*"):
                    break
                fin_exp = j
            return fin_exp
        i += 1

# Analiza cuando se debe crear un nodo del arbol y el nodo se crea con nuevo_nodo()
def analizador_expresion(expresion_regular, indice, padre_actual):
    print("Partial expression:", indice, expresion_regular)

    long_exp = len(expresion_regular)
    i = 0
    while i < long_exp:
        # Si encuentra parentesis es el inicio de una expresion.
        # Contador de cuantos se han abierto o cerrado
        # La operacion tiene que dar 0, abierto +1 cerrado -1
        # Cuando eso es 0 y despues hay un *, + o ? para tomarlo en cuenta en la misma expresión y volver a analizarla con esta función
        if expresion_regular[i] == "(":
            if i == 0:
                cont_parentesis = 1
                for j in range(i+1, long_exp):
                    if expresion_regular[j] == "(":
                        cont_parentesis += 1
                    elif expresion_regular[j] == ")":
                        cont_parentesis -= 1

                    contador = 0
                    if cont_parentesis == 0:
                        if expresion_regular[j] == ")" and j + 1 < long_exp:
                            if expresion_regular[j+1] in operadores:
                                contador += 2

                        fin_exp = j + contador
                        inicio_exp = i + 1
                        padre_actual = analizador_expresion(expresion_regular[inicio_exp:fin_exp], indice, padre_actual)
                        i = j
                        break
            
            # Si encuentra otro parentesis despues de toda la expresion que condiciona el resto, se crea el temporal root, entonces se crea un arbol temporal para concatenarlo al principal
            else:
                if (expresion_regular[i-1] in operadores or expresion_regular[i-1] == ")")  or expresion_regular[i-1] in alfabeto:
                    inicio_exp = i
                    fin_exp = i + 1 + expresiones_en_r(expresion_regular[i:])
                    padre_actual = analizador_expresion(expresion_regular[inicio_exp:fin_exp], len(arboles_temporales), padre_actual)

                    if indice is None:
                        arbol_temporal_i = arboles_temporales.pop()
                    else:
                        arbol_temporal_i = arboles_temporales.pop(indice + 1)


                    if arbol_temporal_i is not None:
                        padre_actual = nuevo_nodo(indice, ".", None, arbol_temporal_i, padre_actual)

                    i = i + fin_exp + 1
        
        # Si encuentra una letra o # 
        elif expresion_regular[i] in alfabeto or expresion_regular[i] == "#":
            # Si no hay temporal head, temporal root ni current head entonces es la primera letra o es la primera letra de una expresion dentro de la expresion principal
            if ((indice is None and padre_actual is None) or i == 0) and i + 1 < long_exp and (expresion_regular[i+1] in alfabeto or expresion_regular[i+1] == "#"):
                # Para expresiones como ab* donde * se aplica solo a la ultima letra. 
                if i + 2 < long_exp and expresion_regular[i+2] in operadores:
                    padre_actual = nuevo_nodo(indice, ".", Arbol(expresion_regular[i]), Arbol(expresion_regular[i+2], Arbol(expresion_regular[i+1]), None), padre_actual)
                    i += 2
                # Si el siguiente caracter es una letra, entonces se unen ambas por medio de un punto como cabeza
                else:
                    padre_actual = nuevo_nodo(indice, ".", Arbol(expresion_regular[i]), Arbol(expresion_regular[i+1]), padre_actual)
                    i += 1
            # Si no hay temp root pero si hay current head o estamos en un lugar dentro de una expresion que no sea la posicion inicial se agrega un punto y el hijo izquierdo es el arbol actual, el derecho es letra actual
            elif (indice is None and padre_actual is not None) or i != 0:
                padre_actual = nuevo_nodo(indice, ".", None, Arbol(expresion_regular[i]), padre_actual)
            else:
                padre_actual = nuevo_nodo(indice, expresion_regular[i], None, None, padre_actual)


            # Para verificar si hay un operador *, + o ? en la expresion y tomarlo en cuenta
            if i + 1 < long_exp:
                if expresion_regular[i+1] in operadores:
                    padre_actual = nuevo_nodo(indice, expresion_regular[i+1], Arbol(expresion_regular[i]), None, padre_actual)
                elif expresion_regular[i+1] == ")":
                    if i + 2 < long_exp:
                        if expresion_regular[i+2] in operadores:
                            padre_actual = nuevo_nodo(indice, expresion_regular[i+2], Arbol(expresion_regular[i]), None, padre_actual)

        # Si es un or, se analiza toda la expresion que esta despues de |, calculando donde finaliza el or.
        # Puede crear arboles temporales que luego de crearse se extraen y se insertan en el arbol principal.
        elif expresion_regular[i] == "|":
            fin_exp = i + 2 + expresiones_en_r(expresion_regular[i+1:])
            padre_actual = analizador_expresion(expresion_regular[i+1:fin_exp], len(arboles_temporales), padre_actual)
            
            # Si existe, se extrae el ultimo arbol temporal 
            if indice is None:
                arbol_temporal_i = arboles_temporales.pop()
            else:
                arbol_temporal_i = arboles_temporales.pop(indice + 1)

            # Inserta el arbol temporal en el arbol principal
            if arbol_temporal_i is not None:
                padre_actual = nuevo_nodo(indice, expresion_regular[i], Arbol(expresion_regular[i-1]), arbol_temporal_i, padre_actual)

            # Analiza si existe un operador *, +, ? para tomarlo en cuenta.
            if fin_exp < long_exp and expresion_regular[fin_exp] == ")":
                if fin_exp + 1 < long_exp:
                    if expresion_regular[fin_exp+1] in operadores:
                        padre_actual = nuevo_nodo(indice, expresion_regular[fin_exp+1], Arbol(expresion_regular[fin_exp+1]), None, padre_actual)

            i = i + fin_exp + 1
        i += 1
    return padre_actual

# Convierte la clase arbol a un arbol tipo BinaryTree
def binarytree(padre, binary_tree_parent=None):
    if binary_tree_parent is None:
        binary_tree_parent = Node(caracteres.index(padre.valor))
        # binary_tree_parent = Node(ord(padre.valor))

    if padre.izquierda is not None and padre.izquierda.valor is not None:
        binary_tree_parent.left = Node(caracteres.index(padre.izquierda.valor))
        # binary_tree_parent.left = Node(ord(padre.izquierda.valor))
        binarytree(padre.izquierda, binary_tree_parent.left)

    if padre.derecha is not None and padre.derecha.valor is not None:
        binary_tree_parent.right = Node(caracteres.index(padre.derecha.valor))
        # binary_tree_parent.right = Node(ord(padre.derecha.valor))
        binarytree(padre.derecha, binary_tree_parent.right)

    return binary_tree_parent


padre_actual = analizador_expresion(r, None, padre_actual)
print(binarytree(padre_actual))


arbol = binarytree(padre_actual)
print(arbol.postorder)



# ------------------------------ Thompson ------------------------------
arbol_postorder = arbol.postorder
dic_estados = {}
alfabeto_exp=[]
dic_transiciones={}
contador_estados = 1

# Diccionario de estados iniciales y finales de cada nodo
for i in arbol_postorder:
    dic_estados[str(contador_estados)] = {
        "Valor": caracteres[i.value],
        "Estado Inicial": None,
        "Estado Final": None,
    }
    i.value = contador_estados
    contador_estados +=1

# Alfabeto que tiene el alfabeto_exp del arbol mas E. Letras de la expresion
for hoja in arbol.leaves:
    for letra in alfabeto:
        if letra == dic_estados[str(hoja.value)]["Valor"]:
            if letra not in alfabeto_exp:
                alfabeto_exp.append(letra)

alfabeto_exp.sort()
alfabeto_exp.append("E")


contador = 1 # S0 = 0 (Inicial)
# Se llena el diccionario con los estados iniciales y finales de cada nodo
for nodo in arbol_postorder:
    # El or crea dos estados mas, dos nodos
    if dic_estados[str(nodo.value)]["Valor"] == "|":
        dic_estados[str(nodo.value)]["Estado Inicial"] = "S"+str(contador)
        contador += 1
        dic_estados[str(nodo.value)]["Estado Final"] = "S"+str(contador)
        contador += 1
    # Concatenación el final del hijo de la izquierda es el inicial del nodo de la derecha; el inicial de la derecha es el final de la izquierda
    elif dic_estados[str(nodo.value)]["Valor"] == ".":
        dic_estados[str(nodo.right.value)]["Estado Inicial"] = dic_estados[str(nodo.left.value)]["Estado Final"] 
        dic_estados[str(nodo.value)]["Estado Inicial"] = dic_estados[str(nodo.left.value)]["Estado Inicial"]
        dic_estados[str(nodo.value)]["Estado Final"] = dic_estados[str(nodo.right.value)]["Estado Final"]
    # Se crean dos estados nuevos como or
    elif dic_estados[str(nodo.value)]["Valor"] == "*":
        dic_estados[str(nodo.value)]["Estado Inicial"] = "S"+str(contador)
        contador += 1
        dic_estados[str(nodo.value)]["Estado Final"] = "S"+str(contador)
        contador += 1
    else:
        dic_estados[str(nodo.value)]["Estado Inicial"] = "S"+str(contador)
        contador += 1
        dic_estados[str(nodo.value)]["Estado Final"] = "S"+str(contador)
        contador += 1

# Estado inicial siempre es S0 pero al que se conecta no siempre es S1 pero si por defecto para luego actualizar este valor
estado_inicial = {
    "Estado Inicial": "S0",
    "Estado Final": "S1"
}
dot = graphviz.Digraph(comment='AFN')
dot.attr(rankdir='LR', size='15')
dot.attr(label="\nAFN: McNaughton-Yamada-Thompson")
dot.attr(fontsize='20')
dot.attr('node', shape='circle')

# Diccionario de transiciones, el contador tiene el maximo de estados
# Para cada estado y cada letra del alfabeto, una lista con cada una de sus transiciones
for i in range(contador):
    dic_transiciones["S"+str(i)]={}
    for letra in alfabeto_exp:
        dic_transiciones["S"+str(i)][letra] = []

for nodo in arbol_postorder:
    # Si es or, se conecta el inicial del or con el inicial de los dos hijos. El final de los hijos se conecta con el final del or
    # Poner estado inicial del or hacia el estado inicial de los hijos. El estado final de los hijos hacie el estado final del or
    if dic_estados[str(nodo.value)]["Valor"] == "|":
        # El final estate de s0 es el inical del or
        if dic_estados[str(nodo.left.value)]["Estado Inicial"] == estado_inicial["Estado Final"]:
            estado_inicial["Estado Final"] = dic_estados[str(nodo.value)]["Estado Inicial"]
        dot.node(str(dic_estados[str(nodo.value)]["Estado Inicial"]), str(dic_estados[str(nodo.value)]["Estado Inicial"]).translate(SUB))
        dot.node(str(dic_estados[str(nodo.left.value)]["Estado Inicial"]), str(dic_estados[str(nodo.left.value)]["Estado Inicial"]).translate(SUB))
        dot.node(str(dic_estados[str(nodo.right.value)]["Estado Inicial"]), str(dic_estados[str(nodo.right.value)]["Estado Inicial"]).translate(SUB))
        dot.edge(dic_estados[str(nodo.value)]["Estado Inicial"], dic_estados[str(nodo.left.value)]["Estado Inicial"], label="E")
        # se guarda la transicion en la tabla de transiciones
        dic_transiciones[dic_estados[str(nodo.value)]["Estado Inicial"]]["E"].append(dic_estados[str(nodo.left.value)]["Estado Inicial"])

        dot.edge(dic_estados[str(nodo.value)]["Estado Inicial"], dic_estados[str(nodo.right.value)]["Estado Inicial"], label="E")
        # se guarda la transicion en la tabla de transiciones
        dic_transiciones[dic_estados[str(nodo.value)]["Estado Inicial"]]["E"].append(dic_estados[str(nodo.right.value)]["Estado Inicial"])

        if dic_estados[str(nodo.value)]["Estado Final"] == "S"+str(contador-1):
            dot.node(str(dic_estados[str(nodo.value)]["Estado Final"]), str(dic_estados[str(nodo.value)]["Estado Final"]).translate(SUB), shape='doublecircle')
        else:
            dot.node(str(dic_estados[str(nodo.value)]["Estado Final"]), str(dic_estados[str(nodo.value)]["Estado Final"]).translate(SUB))
        dot.node(str(dic_estados[str(nodo.left.value)]["Estado Final"]), str(dic_estados[str(nodo.left.value)]["Estado Final"]).translate(SUB))
        dot.node(str(dic_estados[str(nodo.right.value)]["Estado Final"]), str(dic_estados[str(nodo.right.value)]["Estado Final"]).translate(SUB))
        dot.edge(dic_estados[str(nodo.left.value)]["Estado Final"], dic_estados[str(nodo.value)]["Estado Final"], label="E")
        dic_transiciones[dic_estados[str(nodo.left.value)]["Estado Final"]]["E"].append(dic_estados[str(nodo.value)]["Estado Final"])

        dot.edge(dic_estados[str(nodo.right.value)]["Estado Final"], dic_estados[str(nodo.value)]["Estado Final"], label="E")
        dic_transiciones[dic_estados[str(nodo.right.value)]["Estado Final"]]["E"].append(dic_estados[str(nodo.value)]["Estado Final"])

    # El inicial del kleene con el inicial del hijo, el final del hijo con el final de Kleene
    elif dic_estados[str(nodo.value)]["Valor"] == "*":
        if dic_estados[str(nodo.left.value)]["Estado Inicial"] == estado_inicial["Estado Final"]:
            estado_inicial["Estado Final"] = dic_estados[str(nodo.value)]["Estado Inicial"]
        dot.node(str(dic_estados[str(nodo.value)]["Estado Inicial"]), str(dic_estados[str(nodo.value)]["Estado Inicial"]).translate(SUB))
        dot.node(str(dic_estados[str(nodo.left.value)]["Estado Inicial"]), str(dic_estados[str(nodo.left.value)]["Estado Inicial"]).translate(SUB))
        dot.edge(dic_estados[str(nodo.value)]["Estado Inicial"], dic_estados[str(nodo.left.value)]["Estado Inicial"], label="E")
        dic_transiciones[dic_estados[str(nodo.value)]["Estado Inicial"]]["E"].append(dic_estados[str(nodo.left.value)]["Estado Inicial"])

        if dic_estados[str(nodo.value)]["Estado Final"] == "S"+str(contador-1):
            dot.node(str(dic_estados[str(nodo.value)]["Estado Final"]), str(dic_estados[str(nodo.value)]["Estado Final"]).translate(SUB), shape='doublecircle')
        else:
            dot.node(str(dic_estados[str(nodo.value)]["Estado Final"]), str(dic_estados[str(nodo.value)]["Estado Final"]).translate(SUB))
        dot.node(str(dic_estados[str(nodo.left.value)]["Estado Final"]), str(dic_estados[str(nodo.left.value)]["Estado Final"]).translate(SUB))
        dot.edge(dic_estados[str(nodo.left.value)]["Estado Final"], dic_estados[str(nodo.value)]["Estado Final"], label="E")
        dic_transiciones[dic_estados[str(nodo.left.value)]["Estado Final"]]["E"].append(dic_estados[str(nodo.value)]["Estado Final"])

        dot.edge(dic_estados[str(nodo.value)]["Estado Inicial"], dic_estados[str(nodo.value)]["Estado Final"], label="E")
        dic_transiciones[dic_estados[str(nodo.value)]["Estado Inicial"]]["E"].append(dic_estados[str(nodo.value)]["Estado Final"])

        dot.edge(dic_estados[str(nodo.left.value)]["Estado Final"], dic_estados[str(nodo.left.value)]["Estado Inicial"], label="E")
        dic_transiciones[dic_estados[str(nodo.left.value)]["Estado Final"]]["E"].append(dic_estados[str(nodo.left.value)]["Estado Inicial"])

    elif dic_estados[str(nodo.value)]["Valor"] == ".":
        # los hijos de la concatenacion ya tienen la concatenacion
        pass
    # si es letra, se una el estado inicial con el estado final
    else:
        dot.node(str(dic_estados[str(nodo.value)]["Estado Inicial"]),str(dic_estados[str(nodo.value)]["Estado Inicial"]).translate(SUB))
        if str(dic_estados[str(nodo.value)]["Estado Final"]) == "S"+str(contador-1):
            dot.node(str(dic_estados[str(nodo.value)]["Estado Final"]), str(dic_estados[str(nodo.value)]["Estado Final"]).translate(SUB), shape='doublecircle')
        else:
            dot.node(str(dic_estados[str(nodo.value)]["Estado Final"]), str(dic_estados[str(nodo.value)]["Estado Final"]).translate(SUB))
        dot.edge(str(dic_estados[str(nodo.value)]["Estado Inicial"]), str(dic_estados[str(nodo.value)]["Estado Final"]), label=dic_estados[str(nodo.value)]["Valor"])
        dic_transiciones[dic_estados[str(nodo.value)]["Estado Inicial"]][dic_estados[str(nodo.value)]["Valor"]].append(dic_estados[str(nodo.value)]["Estado Final"])

# Se hace el S0 y se conecta
dot.node(str(estado_inicial["Estado Inicial"]), str(estado_inicial["Estado Inicial"]).translate(SUB))
dot.edge(estado_inicial["Estado Inicial"], estado_inicial["Estado Final"], label="E")
dic_transiciones[estado_inicial["Estado Inicial"]]["E"].append(estado_inicial["Estado Final"])

dot.view()

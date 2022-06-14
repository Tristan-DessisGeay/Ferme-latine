#Les imports
from tkinter import *
from tkinter.ttk import *
import tkinter.font as tkFont

import element_controller as ec
import cadwork as cw
import geometry_controller as gc
import visualization_controller as vc
import utility_controller as uc
import attribute_controller as ac

from math import pi,acos

#La classe "FermeLatine"
class FermeLatine():

    #Le constructeur
    def __init__(self,nom,couleur):
        self.nom=nom
        self.couleur=couleur
        self.generee=False
        self.elements={}

        #Entrait moisé
        self.entrait_largeur=120
        self.entrait_hauteur=240
        self.entrait_longueur=7800

        self.entrait_moisement=10

        #Poinçon
        self.poincon_largeur=200
        self.poincon_hauteur=200
        self.poincon_longueur=1500

        #Contre-fiches
        self.contreFiche_largeur=120
        self.contreFiche_hauteur=120
        self.contreFiche_longueur=self.entrait_longueur/2-self.poincon_hauteur/2

        self.contreFiche_espacement=35
        self.contreFiche_angle=20

        #Arbalétriers
        self.arbaletrier_largeur=120
        self.arbaletrier_hauteur=240
        self.arbaletrier_longueur=self.entrait_longueur/2-self.poincon_hauteur/2

        self.arbaletrier_espacement=270
        self.arbaletrier_angle=17

        #Suplément
        self.entrait_espacement=self.arbaletrier_largeur-2*self.entrait_moisement        

    #La méthode principale
    def generer(self):
        #Entrait moisé (1)
        largeur=self.entrait_largeur
        hauteur=self.entrait_hauteur
        longueur=self.entrait_longueur
        p1=cw.point_3d(0,0,0)
        xl=cw.point_3d(1,0,0)
        zl=cw.point_3d(0,0,1)
        self.elements["Entrait1"]=ec.create_rectangular_beam_vectors(largeur,hauteur,longueur,p1,xl,zl)
        elements=[self.elements["Entrait1"]]
        vector=cw.point_3d(0,self.entrait_largeur+self.entrait_espacement,0)
        self.elements["Entrait2"]=ec.copy_elements(elements,vector)[0]

        #Poinçon (2)
        largeur=self.poincon_largeur
        hauteur=self.poincon_hauteur
        longueur=self.poincon_longueur
        p1=cw.point_3d(self.entrait_longueur/2,self.entrait_largeur/2+self.entrait_espacement/2,-self.entrait_hauteur/2)
        xl=cw.point_3d(1,0,0)
        zl=cw.point_3d(0,0,1)
        self.elements["Poinçon"]=ec.create_rectangular_beam_vectors(largeur,hauteur,longueur,p1,xl,zl)
        elements=[self.elements["Poinçon"]]
        origin=gc.get_p1(self.elements["Poinçon"])
        axe=cw.point_3d(0,1,0)
        angle=(pi/180)*-90
        ec.rotate_elements(elements,origin,axe,angle)
        
        #Contre-fiche (3)
        largeur=self.contreFiche_largeur
        hauteur=self.contreFiche_hauteur
        longueur=self.contreFiche_longueur
        p1=cw.point_3d(0,self.entrait_largeur/2+self.entrait_espacement/2,self.entrait_hauteur/2+self.contreFiche_hauteur/2+self.contreFiche_espacement)
        xl=cw.point_3d(1,0,0)
        zl=cw.point_3d(0,0,1)
        self.elements["Contre-fiche1"]=ec.create_rectangular_beam_vectors(largeur,hauteur,longueur,p1,xl,zl)

        elements=[self.elements["Contre-fiche1"]]
        origin=gc.get_element_vertices(self.elements["Contre-fiche1"])[0]
        axe=cw.point_3d(0,1,0)
        angle=(pi/180)*self.contreFiche_angle
        ec.rotate_elements(elements,origin,axe,angle)

        #Arbalétrier (4)
        largeur=self.arbaletrier_largeur
        hauteur=self.arbaletrier_hauteur
        longueur=self.arbaletrier_longueur
        p1=cw.point_3d(0,self.entrait_largeur/2+self.entrait_espacement/2,self.poincon_longueur-self.arbaletrier_hauteur-self.arbaletrier_espacement)
        xl=cw.point_3d(1,0,0)
        zl=cw.point_3d(0,0,1)
        self.elements["Arbalétrier1"]=ec.create_rectangular_beam_vectors(largeur,hauteur,longueur,p1,xl,zl)

        elements=[self.elements["Arbalétrier1"]]
        origin=gc.get_element_vertices(self.elements["Arbalétrier1"])[1]
        axe=cw.point_3d(0,1,0)
        angle=(pi/180)*-self.arbaletrier_angle
        ec.rotate_elements(elements,origin,axe,angle)

        #Subtract (1-2)
        hard_elements=[self.elements["Entrait1"],self.elements["Entrait2"]]
        soft_elements=[self.elements["Poinçon"]]
        ec.subtract_elements(hard_elements,soft_elements)

        #Cut (3-2)
        element=self.elements["Contre-fiche1"]
        normal_vecteur=-gc.get_zl(self.elements["Poinçon"])#Toujours mettre le vecteur du coté de la pièce à couper
        distance=cw.point_3d(0,0,0).distance(gc.get_p1(self.elements["Poinçon"]))
        ec.cut_element_with_plane(element,normal_vecteur,distance)

        #Cut (4-2)
        element=self.elements["Arbalétrier1"]
        normal_vecteur=-gc.get_zl(self.elements["Poinçon"])
        distance=cw.point_3d(0,0,0).distance(gc.get_p1(self.elements["Poinçon"]))
        ec.cut_element_with_plane(element,normal_vecteur,distance)
        
        #Cut (3-4)
        element=self.elements["Contre-fiche1"]
        vecteur=gc.get_zl(self.elements["Arbalétrier1"])
        distance=cw.point_3d(0,0,0).distance(gc.get_p1(self.elements["Arbalétrier1"]))

        if gc.get_p1(self.elements["Arbalétrier1"])[2]<0: distance=-distance#Cette condition est essentielle  

        ec.cut_element_with_plane(element,vecteur,distance)

        #Subtract (3-4)
        hard_element=[self.elements["Arbalétrier1"]]
        soft_element=[self.elements["Contre-fiche1"]]
        ec.subtract_elements(hard_element,soft_element)

        #Subtract (3,4-2)
        hard_element=[self.elements["Poinçon"]]
        soft_elements=[self.elements["Arbalétrier1"],self.elements["Contre-fiche1"]]
        ec.subtract_elements(hard_element,soft_elements)
        
        #Stretch (4)
        element=[self.elements["Arbalétrier1"]]
        point_bas_arbaletrier=gc.get_element_vertices(self.elements["Arbalétrier1"])[5]
        distanceX=-point_bas_arbaletrier[0]*2
        ec.stretch_start_facet(element,cw.point_3d(distanceX,0,0))

        #Cut (4-1)
        ec.cut_element_with_plane(self.elements["Arbalétrier1"],-cw.point_3d(1,0,0),0)

        #Subtract (4-1)
        hard_elements=[self.elements["Entrait1"],self.elements["Entrait2"]]
        soft_element=[self.elements["Arbalétrier1"]]
        ec.subtract_elements(hard_elements,soft_element)

        #Mirror copy
        elements=[self.elements["Contre-fiche1"],self.elements["Arbalétrier1"]]
        vecteur=cw.point_3d(1,0,0)
        distance=self.entrait_longueur/2
        es=ec.mirror_copy_elements(elements,vecteur,distance)
        self.elements["Contre-fiche2"]=es[0]
        self.elements["Arbalétrier2"]=es[1]

        #Noms
        ac.set_name([self.elements["Entrait1"],self.elements["Entrait2"]],"Entrait moisé")
        ac.set_name([self.elements["Poinçon"]], "Poinçon")
        ac.set_name([self.elements["Contre-fiche1"],self.elements["Contre-fiche2"]],"Contre-fiche")
        ac.set_name([self.elements["Arbalétrier1"],self.elements["Arbalétrier2"]],"Arbalétrier")

        self.changer_couleur()
        self.joindre_selection()
        self.changer_nom_groupe()
        self.generee=True

    #Les méthodes complémentaires
    def obtenir_elements_ids(self):
        resultat=[]
        for element, identifiant in self.elements.items():
            resultat.append(identifiant)
        return resultat

    def changer_couleur(self):
        elements=self.obtenir_elements_ids()
        vc.set_color(elements,self.couleur)

    def supprimer(self):
        elements=self.obtenir_elements_ids()
        ec.delete_elements(elements)
        self.generee=False

    def joindre_selection(self):
        elements=self.obtenir_elements_ids()
        ec.join_elements(elements)

    def changer_nom_groupe(self):
        elements=self.obtenir_elements_ids()
        ac.set_group(elements,self.nom)

#Paramétrage fenetre
fenetre=Tk()
fenetre.geometry("600x400")
fenetre.config(bg="pink")
fenetre.title("Ferme Latine")
fenetre.resizable(False,False)
fenetre.attributes("-transparentcolor", "pink")

#Canvas
canvas_attributs_cadre=Canvas(fenetre,background="pink",highlightthickness=0)
canvas_attributs_cadre.place(x=10,y=10,width=275,height=340)

canvas_attributs=Canvas(fenetre,background="white",highlightthickness=0)
canvas_attributs.place(x=15,y=10,width=250,height=335)

canvas_boutons=Canvas(fenetre,highlightthickness=0,background="pink")
canvas_boutons.place(x=10,y=360,width=275,height=30)

canvas_images=Canvas(fenetre,background="pink",highlightthickness=0)
canvas_images.place(x=295,y=10,width=295,height=185)

canvas_historique=Canvas(fenetre,background="pink",highlightthickness=0)
canvas_historique.place(x=295,y=205,width=295,height=185)

canvas_attributs_scroll = Scrollbar(fenetre, orient="vertical", command=canvas_attributs.yview)
canvas_attributs_scroll.place(x=265,y=10,height=335,width=20)
canvas_attributs.configure(yscrollcommand=canvas_attributs_scroll.set)


canvas_boutons_scroll = Scrollbar(fenetre, orient="vertical", command=canvas_boutons.yview)
canvas_boutons_scroll.place(x=-20,y=360,height=30,width=20)
canvas_boutons.configure(yscrollcommand=canvas_boutons_scroll.set)

#Bandeaux bleus
canvas_attributs_cadre.create_polygon(5,-5,0,5,0,340,270,340,275,335,5,335,5,-5,fill="blue")
canvas_historique.create_polygon(290,-2.5,295,5,295,185,5,185,0,180,290,180,290,0,fill="blue")
canvas_images.create_polygon(-5,5,5,0,295,0,295,180,290,185,290,5,0,5,fill="blue")

#Images
attributs_images=[
    PhotoImage(file=uc.get_plugin_path()+"/Images/entrait_largeur.png"),
    PhotoImage(file=uc.get_plugin_path()+"/Images/entrait_hauteur.png"),
    PhotoImage(file=uc.get_plugin_path()+"/Images/entrait_longueur.png"), 
    PhotoImage(file=uc.get_plugin_path()+"/Images/entrait_moisement.png"), 

    PhotoImage(file=uc.get_plugin_path()+"/Images/poinçon_largeur.png"),    
    PhotoImage(file=uc.get_plugin_path()+"/Images/poinçon_hauteur.png"),   
    PhotoImage(file=uc.get_plugin_path()+"/Images/poinçon_longueur.png"),  

    PhotoImage(file=uc.get_plugin_path()+"/Images/contre-fiche_largeur.png"),    
    PhotoImage(file=uc.get_plugin_path()+"/Images/contre-fiche_hauteur.png"),    
    PhotoImage(file=uc.get_plugin_path()+"/Images/contre-fiche_espacement.png"),  
    PhotoImage(file=uc.get_plugin_path()+"/Images/contre-fiche_angle.png"),     

    PhotoImage(file=uc.get_plugin_path()+"/Images/arbalétrier_largeur.png"), 
    PhotoImage(file=uc.get_plugin_path()+"/Images/arbalétrier_hauteur.png"),
    PhotoImage(file=uc.get_plugin_path()+"/Images/arbalétrier_espacement.png"), 
    PhotoImage(file=uc.get_plugin_path()+"/Images/arbalétrier_angle.png")
]

def change_image(e,i): 
    canvas_images.delete("all")
    canvas_images.create_polygon(-5,5,5,0,295,0,295,180,290,185,290,5,0,5,fill="blue")
    canvas_images.create_image(0,5,image=attributs_images[i],anchor="nw")

canvas_images.create_image(0,5,image=attributs_images[0],anchor="nw")

#attributs
liste_attributs={
    "Entraits-moisé":[
        "Largeur",
        "Hauteur",
        "Longueur",
        "Moisement"
    ],
    "Poinçon":[
        "Largeur",
        "Hauteur",
        "Longueur"
    ],
    "Contre-fiches":[
        "Largeur",
        "Hauteur",
        "Espacement",
        "Angle"
    ],
    "Arbalétriers":[
        "Largeur",
        "Hauteur",
        "Espacement",
        "Angle"
    ],
    "Options":[
        "Nom",
        "Couleur"
    ]
}

def couleurs(): liste_champs["Options"][1]["text"]=uc.get_user_color(0)

liste_champs={}
i=0
y=5
for element, attributs in liste_attributs.items():
    canvas_attributs.create_text(5,y,text=element,font=tkFont.Font(size=13),anchor="nw")
    y+=30
    liste_champs[element]=[]
    for attribut in attributs:
        canvas_attributs.create_text(5,y+6,text=attribut,font=tkFont.Font(size=8),anchor="nw")
        if attribut=="Couleur":
            widget=Button(canvas_attributs,cursor="hand2",command=couleurs)
        else:
            widget=Entry(canvas_attributs,font=tkFont.Font(size=8))
            if attribut!="Nom":
                widget.bind("<Button-1>",lambda event, i=i: change_image(event,i))
                i+=1
        liste_champs[element].append(widget)
        canvas_attributs.create_window(200,y,anchor="nw",window=liste_champs[element][-1],width=50,height=30)
        y+=25
    y+=10
liste_champs["Entraits-moisé"][0].focus_set()

#Actualisation de l'interface
canvas_attributs.configure(scrollregion=canvas_attributs.bbox("all"))

#Création d'un premier objet & remplissage des champs
def remplissage_des_champs(ferme):

    #Clear des champs
    for _, champs in liste_champs.items(): 
        for champ in champs:
            if type(champ)==Entry: 
                champ.delete(0,END)

    #Entrait-moisés
    liste_champs["Entraits-moisé"][0].insert(0,ferme.entrait_largeur)
    liste_champs["Entraits-moisé"][1].insert(0,ferme.entrait_hauteur)
    liste_champs["Entraits-moisé"][2].insert(0,ferme.entrait_longueur)
    liste_champs["Entraits-moisé"][3].insert(0,ferme.entrait_moisement)

    #Poiçon
    liste_champs["Poinçon"][0].insert(0,ferme.poincon_largeur)
    liste_champs["Poinçon"][1].insert(0,ferme.poincon_hauteur)
    liste_champs["Poinçon"][2].insert(0,ferme.poincon_longueur)

    #Contre-fiches
    liste_champs["Contre-fiches"][0].insert(0,ferme.contreFiche_largeur)
    liste_champs["Contre-fiches"][1].insert(0,ferme.contreFiche_hauteur)
    liste_champs["Contre-fiches"][2].insert(0,ferme.contreFiche_espacement)
    liste_champs["Contre-fiches"][3].insert(0,ferme.contreFiche_angle)

    #Arbalétriers
    liste_champs["Arbalétriers"][0].insert(0,ferme.arbaletrier_largeur)
    liste_champs["Arbalétriers"][1].insert(0,ferme.arbaletrier_hauteur)
    liste_champs["Arbalétriers"][2].insert(0,ferme.arbaletrier_espacement)
    liste_champs["Arbalétriers"][3].insert(0,ferme.arbaletrier_angle)

    #Options
    liste_champs["Options"][0].insert(0,ferme.nom)
    liste_champs["Options"][1]["text"]=ferme.couleur

ferme1=FermeLatine("Ferme 1",6)

#Historique des fermes
liste_ferme=[]

#Sauvegarde dans les données de projet
def ajouter_listeFerme(ferme):
    data=ferme.nom+":"
    for identifiant in ferme.obtenir_elements_ids(): data+=str(identifiant)+","
    data=data[:-1]
    if uc.get_project_data("Plugin_FermeLatine_elements")!="":
        data=uc.get_project_data("Plugin_FermeLatine_elements")+";"+data
    uc.set_project_data("Plugin_FermeLatine_elements",data)

def supprimer_listeFerme(ferme):
    nouvelle_data=""
    if uc.get_project_data("Plugin_FermeLatine_elements")!="":
        data=uc.get_project_data("Plugin_FermeLatine_elements").split(";")
        for id_ferme in range(len(data)): 
            if data[id_ferme].split(":")[0]!=ferme.nom:
                nouvelle_data+=data[id_ferme]+";"
    uc.set_project_data("Plugin_FermeLatine_elements",nouvelle_data[:-1])

def angle_entre_2_vecteur(v1, v2):
    return acos(v1.dot(v2) / (v1.magnitude() * v2.magnitude())) * (180 /pi)

def maj_listeFerme():

    fermes=uc.get_project_data("Plugin_FermeLatine_elements").split(";")
    for id_ferme in range(len(fermes)):
        fermes[id_ferme]=fermes[id_ferme].split(":")
        fermes[id_ferme][1]=fermes[id_ferme][1].split(",")
        for id_element in range(len(fermes[id_ferme][1])):
            fermes[id_ferme][1][id_element]=int(fermes[id_ferme][1][id_element])
    
        nom=fermes[id_ferme][0]
        couleur=vc.get_color(fermes[id_ferme][1][0])
        nouvelle_ferme=FermeLatine(nom,couleur)

        nouvelle_ferme.elements["Entrait1"]=fermes[id_ferme][1][0]
        nouvelle_ferme.elements["Entrait2"]=fermes[id_ferme][1][1]
        nouvelle_ferme.elements["Poinçon"]=fermes[id_ferme][1][2]
        nouvelle_ferme.elements["Contre-fiche1"]=fermes[id_ferme][1][3]
        nouvelle_ferme.elements["Arbalétrier1"]=fermes[id_ferme][1][4]
        nouvelle_ferme.elements["Contre-fiche2"]=fermes[id_ferme][1][5]
        nouvelle_ferme.elements["Arbalétrier2"]=fermes[id_ferme][1][6]

        #Entrait-moisé
        nouvelle_ferme.entrait_largeur=round(gc.get_width(nouvelle_ferme.elements["Entrait1"]))
        nouvelle_ferme.entrait_hauteur=round(gc.get_height(nouvelle_ferme.elements["Entrait1"]))
        nouvelle_ferme.entrait_longueur=round(gc.get_length(nouvelle_ferme.elements["Entrait1"]))

        a=gc.get_width(nouvelle_ferme.elements["Entrait1"])+gc.get_width(nouvelle_ferme.elements["Arbalétrier1"])
        b=gc.get_p1(nouvelle_ferme.elements["Entrait1"]).distance(gc.get_p1(nouvelle_ferme.elements["Entrait2"]))
        moisement=(a-b)/2
        nouvelle_ferme.entrait_moisement=round(moisement)

        #Poinçon
        nouvelle_ferme.poincon_largeur=round(gc.get_width(nouvelle_ferme.elements["Poinçon"]))
        nouvelle_ferme.poincon_hauteur=round(gc.get_height(nouvelle_ferme.elements["Poinçon"]))
        nouvelle_ferme.poincon_longueur=round(gc.get_length(nouvelle_ferme.elements["Poinçon"]))

        #Contre-fiche
        nouvelle_ferme.contreFiche_largeur=round(gc.get_width(nouvelle_ferme.elements["Contre-fiche1"]))
        nouvelle_ferme.contreFiche_hauteur=round(gc.get_height(nouvelle_ferme.elements["Contre-fiche1"]))
        nouvelle_ferme.contreFiche_longueur=round(nouvelle_ferme.entrait_longueur/2-nouvelle_ferme.poincon_hauteur/2)

        a=gc.get_element_vertices(nouvelle_ferme.elements["Contre-fiche1"])[1][2]
        b=gc.get_p1(nouvelle_ferme.elements["Entrait1"])[2]+nouvelle_ferme.entrait_hauteur/2
        nouvelle_ferme.contreFiche_espacement=round(a-b)

        nouvelle_ferme.contreFiche_angle=round(angle_entre_2_vecteur(gc.get_xl(nouvelle_ferme.elements["Entrait1"]),gc.get_xl(nouvelle_ferme.elements["Contre-fiche1"])))

        #Arbalétrier
        nouvelle_ferme.arbaletrier_largeur=round(gc.get_width(nouvelle_ferme.elements["Arbalétrier1"]))
        nouvelle_ferme.arbaletrier_hauteur=round(gc.get_height(nouvelle_ferme.elements["Arbalétrier1"]))
        nouvelle_ferme.arbaletrier_longueur=round(nouvelle_ferme.entrait_longueur/2-nouvelle_ferme.poincon_hauteur/2)
        
        a=gc.get_p2(nouvelle_ferme.elements["Poinçon"])[2]
        b=gc.get_element_vertices(nouvelle_ferme.elements["Arbalétrier1"])[12][2]
        nouvelle_ferme.arbaletrier_espacement=round(a-b)

        nouvelle_ferme.arbaletrier_angle=round(angle_entre_2_vecteur(gc.get_xl(nouvelle_ferme.elements["Entrait1"]),gc.get_xl(nouvelle_ferme.elements["Arbalétrier1"])))

        #Supplément
        nouvelle_ferme.entrait_espacement=nouvelle_ferme.arbaletrier_largeur-2* nouvelle_ferme.entrait_moisement

        nouvelle_ferme.generee=True
        liste_ferme.append(nouvelle_ferme)
    
    remplissage_des_champs(liste_ferme[0])

#Vérification de l'état actuel de nos données de projet
if uc.get_project_data("Plugin_FermeLatine_elements")=="":
    liste_ferme.append(ferme1)
else: 
    maj_listeFerme()

#Gestion de la listbox d'historique
listBox_historique=Listbox(canvas_historique,exportselection=False,selectmode="single")

def affiche_ferme(*args):
    ferme=liste_ferme[listBox_historique.curselection()[0]]
    remplissage_des_champs(ferme)
    elements=[]
    autres_elements=[]
    for f in liste_ferme:
        if f==ferme: elements+=f.obtenir_elements_ids()
        else: autres_elements+=f.obtenir_elements_ids()
    vc.set_inactive(autres_elements)
    if ferme.generee: 
        vc.set_active(elements)
        canvas_boutons.yview_moveto(40)
    else:
        canvas_boutons.yview_moveto(0)

listBox_historique.bind("<Button-1>",affiche_ferme)
listBox_historique.bind("<ButtonRelease-1>",affiche_ferme)
canvas_historique.create_window(0,0,anchor="nw",window=listBox_historique,width=290,height=180)

def maj_listBox_historique(indice):
    listBox_historique.delete(0,END)
    for ferme in liste_ferme: 
        listBox_historique.insert(END,ferme.nom)
    listBox_historique.select_set(indice)
maj_listBox_historique(0)# On préselectionne la première ferme latine

#Procédure permettantl'actualisation des attributs d'un objet en fonction du contenu des champs de saisi de l'interface
def maj_attributs(ferme):
    #Entrait-moisés
    ferme.entrait_largeur=float(liste_champs["Entraits-moisé"][0].get())
    ferme.entrait_hauteur=float(liste_champs["Entraits-moisé"][1].get())
    ferme.entrait_longueur=float(liste_champs["Entraits-moisé"][2].get())
    ferme.entrait_moisement=float(liste_champs["Entraits-moisé"][3].get())

    #Poinçon
    ferme.poincon_largeur=float(liste_champs["Poinçon"][0].get())
    ferme.poincon_hauteur=float(liste_champs["Poinçon"][1].get())
    ferme.poincon_longueur=float(liste_champs["Poinçon"][2].get())

    #Contre-fiches
    ferme.contreFiche_largeur=float(liste_champs["Contre-fiches"][0].get())
    ferme.contreFiche_hauteur=float(liste_champs["Contre-fiches"][1].get())
    ferme.contreFiche_espacement=float(liste_champs["Contre-fiches"][2].get())
    ferme.contreFiche_angle=float(liste_champs["Contre-fiches"][3].get())

    #Arbalétriers
    ferme.arbaletrier_largeur=float(liste_champs["Arbalétriers"][0].get())
    ferme.arbaletrier_hauteur=float(liste_champs["Arbalétriers"][1].get())
    ferme.arbaletrier_espacement=float(liste_champs["Arbalétriers"][2].get())
    ferme.arbaletrier_angle=float(liste_champs["Arbalétriers"][3].get())

    #Options
    nom=liste_champs["Options"][0].get()
    if ferme.nom!=nom:
        ferme.nom=nom
        maj_listBox_historique(listBox_historique.curselection()[0])
    ferme.couleur=int(liste_champs["Options"][1]["text"])

#Boutons
def generer():
    ferme=liste_ferme[listBox_historique.curselection()[0]]
    ok=True
    for element,attributs in liste_champs.items():
        for attribut in attributs:
            if type(attribut)==Entry and attribut.get()=="": 
                ok=False
                break
        if not ok: break
    if ok:
        maj_attributs(ferme)
        ferme.generer()
        ajouter_listeFerme(ferme)
        affiche_ferme()
        
bouton_generer=Button(canvas_boutons,text="Générer",cursor="hand2",command=generer)
canvas_boutons.create_window(0,0,anchor="nw",window=bouton_generer,width=275,height=30)

def nouvelle():
    dialogue=Toplevel(fenetre)# "Toplevel" permet de créer une fenêtre fille
    dialogue.geometry("300x100")
    dialogue.resizable(False,False)
    dialogue.title("Nouvelle Ferme Latine")

    Label(dialogue,text="Nom").place(x=10,y=10,height=30)
    nom=Entry(dialogue)
    nom.place(x=190,y=10,width=100,height=30)

    def creer():
        if nom.get()!="":
            ok=True
            for ferme in liste_ferme:
                if ferme.nom==nom.get():
                    ok=False
                    break
            if ok:
                ferme=FermeLatine(nom.get(),6)
                liste_ferme.append(ferme)
                maj_listBox_historique(END)
                affiche_ferme()
                dialogue.destroy()

    Button(dialogue,text="Créer",command=creer,cursor="hand2").place(x=100,y=60,width=100,height=30)

bouton_nouveau=Button(canvas_boutons,text="Nouvelle",cursor="hand2",command=nouvelle)
canvas_boutons.create_window(0,40,anchor="nw",window=bouton_nouveau,width=88,height=30)

def modifier():
    ferme=liste_ferme[listBox_historique.curselection()[0]]
    ferme.supprimer()
    supprimer_listeFerme(ferme)
    generer()
        
bouton_modifier=Button(canvas_boutons,text="Modifier",cursor="hand2",command=modifier)
canvas_boutons.create_window(94,40,anchor="nw",window=bouton_modifier,width=88,height=30)

def supprimer():
    ferme=liste_ferme[listBox_historique.curselection()[0]]
    ferme.supprimer()
    supprimer_listeFerme(ferme)
    if len(liste_ferme)>1:
        liste_ferme.remove(ferme)
        maj_listBox_historique(END)
    affiche_ferme()

bouton_supprimer=Button(canvas_boutons,text="Supprimer",cursor="hand2",command=supprimer)
canvas_boutons.create_window(187,40,anchor="nw",window=bouton_supprimer,width=88,height=30)

#Actualisation de l'interface
canvas_boutons.configure(scrollregion=canvas_boutons.bbox("all"))
affiche_ferme()

#Boucle principale
fenetre.mainloop()
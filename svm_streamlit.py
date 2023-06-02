import streamlit as st
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn import svm
from sklearn.metrics import accuracy_score


def main():
    st.title("Application de prédiction de sentiment")
    
    # Charger les données
    d = pd.read_csv('final_data.csv')  # Remplacez 'votre_fichier.csv' par le nom de votre fichier de données
    
    # Préparation des données
    X = d['review_text']
    y = d['sentiment']
    
    # Séparation des données en ensembles d'entraînement et de test
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Convertir X_train en liste de chaînes de caractères
    X_train = X_train.tolist()
    X_train = [str(texte) for texte in X_train]
    
    # Convertir X_test en liste de chaînes de caractères
    X_test = X_test.tolist()
    X_test = [str(texte) for texte in X_test]
    
    # Création d'un vecteur TF-IDF pour représenter les caractéristiques
    vectorizer = TfidfVectorizer()
    X_train = vectorizer.fit_transform(X_train)
    X_test = vectorizer.transform(X_test)
    
    # Entraînement du modèle SVM
    model = svm.SVC(kernel='linear')
    model.fit(X_train, y_train)
    
    # Saisie du commentaire dans une zone de texte
    comment = st.text_input("Saisissez votre commentaire", "")
    
    if st.button("Prédire"):
        if comment:
            # Prétraitement du commentaire
            comment = [comment]
            comment = vectorizer.transform(comment)
            
            # Prédiction sur le commentaire
            prediction = model.predict(comment)
            
            st.write("Sentiment prédit : ", prediction[0])
        else:
            st.write("Veuillez saisir un commentaire.")

if __name__ == '__main__':
    main()

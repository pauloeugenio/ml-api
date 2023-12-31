from flask import Flask, jsonify, render_template, send_file
import csv
import mysql.connector
import random
import pandas as pd
from sklearn.neighbors import KNeighborsRegressor
from sklearn.neural_network import MLPClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.tree import DecisionTreeRegressor
from sklearn.svm import SVR
from sklearn.metrics import accuracy_score, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns
import io

app = Flask(__name__)

@app.route('/consulta', methods=['GET'])
def consultar_dados():
    try:
        # Conecta ao banco de dados MySQL
        conn = mysql.connector.connect(
            host='172.18.1.9',
            port=3306,
            user='user',
            password='senha',
            database='bd'
        )
        cursor = conn.cursor()

        # Executa a consulta dos últimos 20 dados da tabela
        cursor.execute('SELECT voltA AS voltA, voltB, voltC, correnteA, correnteB, correnteC, (voltA * correnteA) AS potenciaA, (voltB * correnteB) AS potenciaB, (voltC * correnteC) AS potenciaC from SM_002_Sensor LIMIT 20')
        data = cursor.fetchall()

        # Obtém os nomes das colunas
        field_names = [i[0] for i in cursor.description]

        # Gera um arquivo CSV com os dados
        with open('consulta.csv', 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(field_names)
            writer.writerows(data)

        # Lê o arquivo CSV gerado
        df = pd.read_csv('consulta.csv')

        # Remove 50% dos dados de forma aleatória
        df = df.sample(frac=0.5, random_state=42)

        # Separa os dados de entrada (X) e saída (y)
        X = df[['voltA', 'voltB', 'voltC', 'correnteA', 'correnteB', 'correnteC']]
        y = df['potenciaA'].astype('int')

        # Dicionário para armazenar os resultados dos algoritmos
        results = {}

        # KNN
        knn = KNeighborsRegressor()
        knn.fit(X, y)
        knn_predictions = knn.predict(X)
        knn_accuracy = accuracy_score(y, knn_predictions.round())
        knn_confusion_matrix = confusion_matrix(y, knn_predictions.round())
        results['knn'] = {'predictions': knn_predictions.tolist(), 'accuracy': knn_accuracy, 'confusion_matrix': knn_confusion_matrix.tolist()}

        # MLP
        mlp = MLPClassifier()
        mlp.fit(X, y)
        mlp_predictions = mlp.predict(X)
        mlp_accuracy = accuracy_score(y, mlp_predictions.round())
        mlp_confusion_matrix = confusion_matrix(y, mlp_predictions.round())
        results['mlp'] = {'predictions': mlp_predictions.tolist(), 'accuracy': mlp_accuracy, 'confusion_matrix': mlp_confusion_matrix.tolist()}

        # Naive Bayes
        nb = GaussianNB()
        nb.fit(X, y)
        nb_predictions = nb.predict(X)
        nb_accuracy = accuracy_score(y, nb_predictions.round())
        nb_confusion_matrix = confusion_matrix(y, nb_predictions.round())
        results['naive_bayes'] = {'predictions': nb_predictions.tolist(), 'accuracy': nb_accuracy, 'confusion_matrix': nb_confusion_matrix.tolist()}

        # Árvore de Decisão
        dt = DecisionTreeRegressor()
        dt.fit(X, y)
        dt_predictions = dt.predict(X)
        dt_accuracy = accuracy_score(y, dt_predictions.round())
        dt_confusion_matrix = confusion_matrix(y, dt_predictions.round())
        results['decision_tree'] = {'predictions': dt_predictions.tolist(), 'accuracy': dt_accuracy, 'confusion_matrix': dt_confusion_matrix.tolist()}

        # SVM
        svm = SVR()
        svm.fit(X, y)
        svm_predictions = svm.predict(X)
        svm_accuracy = accuracy_score(y, svm_predictions.round())
        svm_confusion_matrix = confusion_matrix(y, svm_predictions.round())
        results['svm'] = {'predictions': svm_predictions.tolist(), 'accuracy': svm_accuracy, 'confusion_matrix': svm_confusion_matrix.tolist()}

        cursor.close()
        conn.close()

        # Gera um novo arquivo CSV com os dados filtrados
        filtered_data = df[['voltA', 'voltB', 'voltC', 'correnteA', 'correnteB', 'correnteC', 'potenciaA']]
        filtered_data.to_csv('consulta_filtrada.csv', index=False)

        # Salvar matrizes de confusão como imagens
        for algorithm, result in results.items():
            cm = result['confusion_matrix']
            labels = sorted(list(set(y)))
            plt.figure(figsize=(8, 6))
            sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=labels, yticklabels=labels)
            plt.title(f"Confusion Matrix - {algorithm}")
            plt.xlabel("Predicted")
            plt.ylabel("True")
            plt.savefig(f"static/{algorithm}_confusion_matrix.png")
            plt.close()

        return render_template('results.html', results=results)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/images/<path:filename>')
def send_image(filename):
    return send_file(f'static/{filename}', mimetype='image/png')

if __name__ == '__main__':
    app.run(host='0.0.0.0')

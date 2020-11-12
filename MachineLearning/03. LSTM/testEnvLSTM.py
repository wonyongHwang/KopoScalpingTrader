#!/usr/bin/env python
# coding: utf-8

# In[1]:


#!/usr/bin/env python
# coding: utf-8

# ### 기본 라이브러리 설정

import pandas as pd
from tensorflow.keras.layers import LSTM
import tensorflow.keras.backend as K
from sklearn.preprocessing import MinMaxScaler
import warnings
import os
os.environ['KMP_DUPLICATE_LIB_OK']='True'


script_dir = os.getcwd() # os.path.dirname(__file__)
results_dir = os.path.join(script_dir, 'Results/')


warnings.filterwarnings(action="ignore")

if not os.path.isdir(results_dir):
    os.makedirs(results_dir)

# ### 1~2. 데이터 불러오기 및 분리
# 데이터 불러오기 및 정렬
featureData = pd.read_csv('../dataset/t1471oboccurs.csv')
sortKey = ["shcode","date","time"]

featureData = featureData.sort_values(sortKey)
featureData.head()

# 종목 번호 설정 (TODO: 종목번호 외부 파라미터로 전달처리하도록 인터페이스 노출)
g_shCode = 270

# 특정 주차 기준 분리
predictStd = 150000
train_dataset = featureData[(featureData.time <= predictStd) & (featureData.shcode == g_shCode)]
test_dataset = featureData[(featureData.time > predictStd) & (featureData.shcode == g_shCode)]

print(train_dataset.head())

# 인덱스 초기화
train_dataset = train_dataset.reset_index(drop=True)
test_dataset = test_dataset.reset_index(drop=True)

# 답지 별도 분리
train_labels = train_dataset["close"]
test_labels = test_dataset["close"]
train_dataset.head()

test_dataset.head()

train_dataset.columns

features  = ["close"]

train_dataset = train_dataset.dropna()
test_dataset = test_dataset.dropna()

trainingData_features = train_dataset[features]
trainingData_features


scaler = MinMaxScaler()
df_scaled = scaler.fit_transform(trainingData_features)
df_scaled


df_scaled = pd.DataFrame(df_scaled)
df_scaled.columns = ['close']
df_scaled


trainingData_features = df_scaled
trainingData_features


testData_features = test_dataset[features]
df_scaled = scaler.fit_transform(testData_features)
df_scaled = pd.DataFrame(df_scaled)
df_scaled.columns = ['close']
testData_features = df_scaled
testData_features


testData_all = test_dataset

for s in range(1, 13):
    trainingData_features['shift_{}'.format(s)] = trainingData_features['close'].shift(s)
    testData_features['shift_{}'.format(s)] = testData_features['close'].shift(s)

trainingData_features.head()


#결측치 대체
#trainingData_features = trainingData_features.where(pd.isnull(trainingData_features), trainingData_features.mean(), axis='columns')
trainingData_features = trainingData_features.fillna(trainingData_features.mean())
trainingData_features

#결측치 대체
#trainingData_features = trainingData_features.where(pd.isnull(trainingData_features), trainingData_features.mean(), axis='columns')
testData_features = testData_features.fillna(trainingData_features.mean())
testData_features


tempTrData = trainingData_features

trainingData_features = tempTrData.dropna().drop('close', axis=1)
trainingData_label = tempTrData.dropna()[['close']]
# print("---------------------------")
# print(trainingData_features.head())
# print("---------------------------")
# print(trainingData_label.head)

print(testData_features)
tempTsData = testData_features.dropna()

# print(tempTsData)
testData_features = tempTsData.drop('close', axis=1)
testData_label = tempTsData[['close']]
# print(testData_features.head())
# print(test_labels.head())
print(testData_features)

trainingData_features = trainingData_features.values
trainingData_label = trainingData_label.values
testData_features = testData_features.values
testData_label = testData_label.values
print(testData_features)


#trainingData_features = np.reshape(trainingData_features, (trainingData_features.shape[0], 12, len(features))) # 샘플 수, 타임스텝 수, 속성 수
trainingData_features = trainingData_features.reshape(trainingData_features.shape[0],  12,1) # 각각의 차원은 (size, timestep, feature)
trainingData_features = K.cast(trainingData_features, dtype='float64')
trainingData_label = K.cast(trainingData_label, dtype = 'float64')
print(trainingData_features.shape)
print("---------------------------")
print(trainingData_features)
print("---------------------------")
print(trainingData_label)


# print(trainingData_features)
testData_features = testData_features.reshape(testData_features.shape[0], 12,1) # 각각의 차원은 (size, timestep, feature)
testData_features = K.cast(testData_features, dtype='float64')
testData_label = K.cast(testData_label, dtype='float64')
print(testData_features.shape)
print("---------------------------")
print(testData_features)
print("---------------------------")
print(testData_label)

from tensorflow.keras import Sequential
from tensorflow.keras.layers import Dense


trainingData_features.shape
#print(len(features))


K.clear_session
model = Sequential()
### 4개의 feature 가 행으로 입력됨
# model.add(Dense(8, activation='relu', input_shape=(len(features),)))
# model.add(Dense(8, activation='relu'))
# model.add(Dense(1))

model.add(LSTM(20, return_sequences=True,input_shape=(12,1))) # (timestep, feature)

model.add(LSTM(20, return_sequences=False))

model.add(Dense(1, activation='linear'))

model.compile(loss='mean_squared_error', optimizer='adam')

# ### 4. 모델 컴파일
model.summary()


from tensorflow.keras.callbacks import EarlyStopping
#더이상 에러율이 향상되지 않을 시 정지한다, 단 patience 옵션 유지(너무빨리 끝나는거 방지)
# early_stopping_monitor = EarlyStopping(patience=500)

early_stopping_monitor = EarlyStopping(monitor='loss', patience=1, verbose=1)
EPOCHS = 50
#모델 훈련 (훈련/검증을 80%, 20%로 나눔)
history = model.fit(trainingData_features, trainingData_label, epochs=EPOCHS, batch_size=30, validation_split=0.2, verbose=1, callbacks=[early_stopping_monitor])

print(pd.DataFrame(history.history))
import matplotlib.pyplot as plt

plt.figure(figsize=(12,8))
# 훈련 데이터의 mse
plt.plot(history.history['loss'])
# 검증 데이터의 mse
plt.plot(history.history['val_loss'])
plt.legend(['loss','val_loss'])
plt.grid()
#plt.show()
plt.savefig(results_dir+'figError.png', dpi=300)


pd.DataFrame(history.history)


# ### 6. 모델 추론

loss = model.evaluate(testData_features, testData_label, verbose=0)

# ### 7. 예측

print(testData_features)


test_predictions = model.predict(testData_features).flatten()
# print(test_predictions)
#test_predictions


# 예측결과 별도 데이터프레임 생성
predictValues = pd.DataFrame(list(test_predictions), columns = ["PREDICT"])
print(predictValues)
predictValues = scaler.inverse_transform(predictValues)
predictValues


predictValues = pd.DataFrame(predictValues)
predictValues.columns = ['PREDICT']
predictValues = predictValues
predictValues


# predictValues = pd.Series(test_predictions, name='PREDICT')
# print(predictValues)
# 예측결과 컬럼 생성
finalResult = pd.concat([testData_all,predictValues],axis=1)
print(finalResult)


# ### 8. 예측결과 비교 (시각화)
#finalResult = finalResult.dropna()
print(finalResult)


#finalResult.loc[0]
tempCodes = finalResult.drop_duplicates(['shcode'])

for code in tempCodes['shcode']:
    #print(code)
    plt.title(code)
    plt.figure(figsize=(10,5))
    plt.plot(finalResult.time[finalResult.shcode == code ], finalResult.close[finalResult.shcode == code], label = "close")
    plt.plot(finalResult.time[finalResult.shcode == code ], finalResult.PREDICT[finalResult.shcode == code], label = "predict")
    plt.legend(loc=0)
    plt.savefig(results_dir+'fig'+str(code)+'.png', dpi=300)



# ### 모델 저장 및 재학습

# 모델 저장
model_json = model.to_json()

with open(str(g_shCode)+"_model.json", "w") as json_file:
    json_file.write(model_json)

model.save_weights(str(g_shCode)+"_learning_weights.h5")


#model.save("linear_keras_sellout2.h5")





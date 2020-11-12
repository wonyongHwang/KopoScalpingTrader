#!/usr/bin/env python
# coding: utf-8

# ### 기본 라이브러리 설정

# In[1]:


# 라이브러리 정의 import tensorflow.keras
#import keras
from tensorflow import keras
#from keras import layers
import numpy as np
import pandas as pd
import os
import warnings
import os
os.environ['KMP_DUPLICATE_LIB_OK']='True'


script_dir = os.path.dirname(__file__)
results_dir = os.path.join(script_dir, 'Results/')


warnings.filterwarnings(action="ignore")

if not os.path.isdir(results_dir):
    os.makedirs(results_dir)

# ### 1~2. 데이터 불러오기 및 분리

# In[4]:


# 데이터 불러오기 및 정렬
featureData = pd.read_csv('../dataset/t1471oboccurs.csv')
sortKey = ["shcode","date","time"]

featureData = featureData.sort_values(sortKey)
featureData.head()
# 숫자형 컬럼 생성
#featureData["HOLIDAY_YN"] = np.where(featureData.HOLIDAY=="Y",1,0)
#featureData["PROMOTION_YN"] = np.where(featureData.PROMOTION=="Y",1,0)


# In[10]:


# 특정 주차 기준 분리
predictStd = 150000
train_dataset = featureData[featureData.time <= predictStd]
test_dataset = featureData[featureData.time > predictStd]

# 특정 주차 기준 분리
# predictStd = 201630
# train_dataset = featureData.query('YEARWEEK <= @predictStd')
# test_dataset = featureData.query('YEARWEEK > @predictStd’)
train_dataset.head()


# In[11]:


# 인덱스 초기화
train_dataset = train_dataset.reset_index(drop=True)
test_dataset = test_dataset.reset_index(drop=True)

# 답지 별도 분리
train_labels = train_dataset["close"]
test_labels = test_dataset["close"]
train_dataset.head()


# In[12]:


test_dataset.head()


# In[13]:


train_dataset.columns


# In[14]:


# feature / label 선정 다른 풀이
# label = ["QTY"]
# features = list(featuresData.select_dtypes(np.number).columns)
# features = list(set(features)-set(label))


# In[16]:


features  = ["offerrem1","offerho1","bidrem1","bidho1"]
label = ['close']


# In[17]:


trainingData_features = train_dataset[features]
trainingData_label = train_dataset[label]
testData_features = test_dataset[features]
testData_label = test_dataset[label]
testData_all = test_dataset


# In[18]:


len(features)


# ### 3. 모델 생성

# In[19]:


from tensorflow.keras import Sequential
from tensorflow.keras.layers import Dense


# In[22]:


trainingData_features.shape
#print(len(features))


# In[23]:


model = Sequential()
### 4개의 feature 가 행으로 입력됨
model.add(Dense(8, activation='relu', input_shape=(len(features),)))
model.add(Dense(8, activation='relu'))
model.add(Dense(1))


# ### 4. 모델 컴파일

# In[24]:


#optimizer = keras.optimizers.RMSprop(0.001)
optimizer = keras.optimizers.Adam()
model.compile(loss='mean_squared_error',
                optimizer=optimizer,
                metrics=['mean_absolute_error','mean_squared_error'])


model.summary()


# ### 5. 모델 훈련

# In[25]:


from tensorflow.keras.callbacks import EarlyStopping
#더이상 에러율이 향상되지 않을 시 정지한다, 단 patience 옵션 유지(너무빨리 끝나는거 방지)
early_stopping_monitor = EarlyStopping(patience=500)
EPOCHS = 300
#모델 훈련 (훈련/검증을 80%, 20%로 나눔)
history =model.fit(trainingData_features,
                   trainingData_label,
                   validation_split=0.2, epochs= EPOCHS, callbacks=[early_stopping_monitor])


import matplotlib.pyplot as plt
#get_ipython().run_line_magic('matplotlib', 'inline')

plt.figure(figsize=(12,8))
# 훈련 데이터의 mse
plt.plot(history.history['mean_squared_error'])
# 검증 데이터의 mse
plt.plot(history.history['val_mean_squared_error'])
plt.legend(['mse','val_mse'])
plt.grid()
#plt.show()
plt.savefig(results_dir+'figError.png', dpi=300)




# In[28]:


pd.DataFrame(history.history)


# ### 6. 모델 추론

# In[29]:


loss, mae, mse = model.evaluate(testData_features, testData_label, verbose=0)


# In[30]:


#model.evaluate(testData_features, testData_label, verbose=0)


# In[31]:


np.sqrt(mse)


# ### 7. 예측

# In[35]:


test_predictions = model.predict(testData_features).flatten()
#test_predictions


# In[36]:


# 예측결과 별도 데이터프레임 생성
predictValues = pd.DataFrame(list(test_predictions), columns = ["PREDICT"])

# 예측결과 컬럼 생성
finalResult = pd.concat([testData_all,predictValues],axis=1)
finalResult.head()


# ### 8. 예측결과 비교 (시각화)



#finalResult.loc[0]
tempCodes = finalResult.drop_duplicates(['shcode'])
#tempCodes


# In[51]:


for code in tempCodes['shcode']:
    #print(code)
    plt.title(code)
    plt.figure(figsize=(10,5))
    plt.plot(finalResult.time[finalResult.shcode == code], finalResult.close[finalResult.shcode == code], label = "close")
    plt.plot(finalResult.time[finalResult.shcode == code], finalResult.PREDICT[finalResult.shcode == code], label = "predict")
    plt.legend(loc=0)
    plt.savefig(results_dir+'fig'+str(code)+'.png', dpi=300)



# ### 모델 저장 및 재학습

# In[53]:


# 모델 저장
model_json = model.to_json()

with open("model.json", "w") as json_file:
    json_file.write(model_json)

model.save_weights("linear_keras_sellout.h5")


# In[54]:


model.save("linear_keras_sellout2.h5")


# In[36]:


from tensorflow.keras.models import model_from_json
json_file = open("model.json", "r")
loaded_model_json = json_file.read()
json_file.close()

loaded_model = model_from_json(loaded_model_json)
loaded_model.load_weights("linear_keras_sellout.h5")


# In[37]:


#모델 재 컴파일
optimizer= keras.optimizers.Adam()

loaded_model.compile(loss='mean_squared_error',
                     optimizer=optimizer,
                     metrics=['mean_absolute_error','mean_squared_error'])
loaded_model.summary()


# In[38]:



from tensorflow.keras.callbacks import EarlyStopping
#더이상 에러율이 향상되지 않을 시 정지한다, 단 patience 옵션 유지(너무빨리 끝나는거 방지)
early_stopping_monitor = EarlyStopping(patience=50)
EPOCHS = 100
#모델 훈련 (훈련/검증을 80%, 20%로 나눔)
history =loaded_model.fit(trainingData_features,
                   trainingData_label,
                   validation_split=0.2, epochs= EPOCHS, callbacks=[early_stopping_monitor])


# In[39]:


test_predictions = model.predict(testData_features).flatten()

# 예측결과 별도 데이터프레임 생성
predictValues = pd.DataFrame(list(test_predictions), columns = ["PREDICT"])

# 예측결과 컬럼 생성
finalResult = pd.concat([testData_all,predictValues],axis=1)
finalResult.head()

tempCodes = finalResult.drop_duplicates(['shcode'])
for code in tempCodes['shcode']:
    # print(code)
    plt.title(code)
    plt.figure(figsize=(10, 5))
    plt.plot(finalResult.time[finalResult.shcode == code], finalResult.close[finalResult.shcode == code], label="close")
    plt.plot(finalResult.time[finalResult.shcode == code], finalResult.PREDICT[finalResult.shcode == code],
             label="predict")
    plt.legend(loc=0)
    plt.savefig(results_dir+'ResultFig'+str(code)+'.png', dpi=300)






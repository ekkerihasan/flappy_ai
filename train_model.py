# train_tf.py
import pandas as pd
import numpy as np
import os
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import joblib
import tensorflow as tf
from tensorflow.keras import layers, models, callbacks

# load best available CSV
if os.path.exists("training_data_improved.csv"):
    path = "training_data_improved.csv"
elif os.path.exists("training_data.csv"):
    path = "training_data.csv"
else:
    raise SystemExit("No training CSV found. Run record_game_improved.py first.")

print("Loading", path)
df = pd.read_csv(path)

# if old CSV (no extra columns), compute distance and gap_center
if "distance_to_pipe" not in df.columns:
    df["distance_to_pipe"] = df["pipe_x"] - 50
if "gap_center" not in df.columns:
    df["gap_center"] = (df["top_pipe_y"] + df["bottom_pipe_y"]) / 2.0
if "gap_size" not in df.columns:
    df["gap_size"] = df["bottom_pipe_y"] - df["top_pipe_y"]

# choose features
FEATURES = ["bird_y", "top_pipe_y", "bottom_pipe_y", "pipe_x", "distance_to_pipe", "gap_center", "gap_size"]
# some old CSVs use slightly different names; try alternatives
for col in FEATURES:
    if col not in df.columns:
        # try legacy names
        if col == "top_pipe_y" and "pipe_top" in df.columns:
            df["top_pipe_y"] = df["pipe_top"]
        if col == "bottom_pipe_y" and "pipe_bottom" in df.columns:
            df["bottom_pipe_y"] = df["pipe_bottom"]
        if col == "pipe_x" and "pipe_x" not in df.columns:
            # maybe older files used 'pipe_x' already; otherwise error later
            pass

# final check
X = df[FEATURES].astype(float).values
y = df["action"].astype(int).values

print("Dataset shape:", X.shape, "Labels:", np.bincount(y))

# split
X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.15, random_state=42, stratify=y)

# scaler
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_val = scaler.transform(X_val)

joblib.dump(scaler, "scaler.joblib")
print("Scaler saved to scaler.joblib")

# build model
def build_model(input_dim):
    model = models.Sequential()
    model.add(layers.Input(shape=(input_dim,)))
    model.add(layers.Dense(128, activation="relu"))
    model.add(layers.Dropout(0.25))
    model.add(layers.Dense(64, activation="relu"))
    model.add(layers.Dropout(0.2))
    model.add(layers.Dense(32, activation="relu"))
    model.add(layers.Dense(1, activation="sigmoid"))  # output probability of jump
    model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=1e-3),
                  loss="binary_crossentropy",
                  metrics=["accuracy"])
    return model

model = build_model(X_train.shape[1])
model.summary()

# callbacks
es = callbacks.EarlyStopping(monitor="val_loss", patience=7, restore_best_weights=True)
mc = callbacks.ModelCheckpoint("tf_model.h5", monitor="val_loss", save_best_only=True)

history = model.fit(
    X_train, y_train,
    validation_data=(X_val, y_val),
    epochs=80,
    batch_size=64,
    callbacks=[es, mc],
    verbose=2
)

# save final model (best already saved by checkpoint)
model.save("tf_model.h5")
print("Model saved to tf_model.h5")

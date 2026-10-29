import cv2

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

for i in range(100):
    ok, frame = cap.read()
    if ok:
        cv2.imshow("Test", frame)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
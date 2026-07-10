const { initializeTestEnvironment, assertFails, assertSucceeds } = require("@firebase/rules-unit-testing");
const { doc, setDoc } = require("firebase/firestore");
const fs = require("fs");
const path = require("path");

const PROJECT_ID = "smartarena-test-rules";

let testEnv;

before(async () => {
  testEnv = await initializeTestEnvironment({
    projectId: PROJECT_ID,
    firestore: {
      host: "127.0.0.1",
      port: 9090,
      rules: fs.readFileSync(
        path.resolve(__dirname, "../../firebase/firestore.rules"),
        "utf-8"
      ),
    },
  });
});

after(async () => {
  await testEnv.cleanup();
});

describe("Firestore Security Rules", () => {
  describe("/users/{uid}", () => {
    it("fan cannot elevate their own role", async () => {
      const db = testEnv.authenticatedContext("user1").firestore();
      const userRef = doc(db, "users/user1");

      await assertSucceeds(
        setDoc(userRef, { email: "a@b.com", name: "Fan" })
      );

      await assertFails(
        setDoc(userRef, { role: "admin" }, { merge: true })
      );
    });
  });

  describe("/crowd_data", () => {
    it("non-admin cannot write to crowd_data", async () => {
      const db = testEnv.authenticatedContext("user1", { role: "fan" }).firestore();
      const ref = doc(db, "crowd_data/doc1");
      await assertFails(setDoc(ref, { zones: [] }));
    });
  });

  describe("/sustainability", () => {
    it("non-admin cannot write to sustainability", async () => {
      const db = testEnv.authenticatedContext("user1", { role: "fan" }).firestore();
      const ref = doc(db, "sustainability/doc1");
      await assertFails(setDoc(ref, { metrics: {} }));
    });
  });

  describe("/predictions", () => {
    it("rejects all client writes", async () => {
      const adminDb = testEnv.authenticatedContext("admin1", { role: "admin" }).firestore();
      const ref = doc(adminDb, "predictions/doc1");
      await assertFails(setDoc(ref, { result: "test" }));
    });
  });
});

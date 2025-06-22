import { useContext, useState } from "react";
import { Context } from "..";
import { doc, getDoc, increment, updateDoc } from "firebase/firestore";

const Add = () => {
  const ctx = useContext(Context);
  const [addValue, setAddValue] = useState(0);
  const [adding, setAdding] = useState(false);

  if (ctx.user) {
    const docRef = doc(ctx.db, "Users", ctx.user.uid);

    getDoc(docRef).then((docSnap) => {
      console.log(docSnap);
      if (docSnap.exists()) {
        const data = docSnap.data();

        ctx.setBearBucks(data.bearBucks);
      } else {
        // docSnap.data() will be undefined in this case
        console.log("No such document!");
      }
    });
  }

  const addHandler = () => {
    if (!adding) {
      setAdding(true);
      const userRef = doc(ctx.db, "Users", ctx.user.uid);
      updateDoc(userRef, { bearBucks: increment(addValue) }).then(() => {
        ctx.setBearBucks(Number(ctx.bearBucks) + Number(addValue));
        setAdding(false);
        console.log("updated");
      });
    }
  };

  return (
    <div className="p-10 items-center flex flex-col gap-10">
      <p className="font-bold text-7xl">Add</p>
      <div className="gap-2 flex">
        <label>Amount:</label>
        <input
          onChange={(e) => setAddValue(e.target.value)}
          value={addValue}
          className="border-b"
        />
        <label>Bear Bucks</label>
      </div>
      <button
        type="button"
        onClick={addHandler}
        className="bg-white/25 p-2 rounded-md"
      >
        Add Bear Bucks
      </button>
    </div>
  );
};

export default Add;

import { useContext, useState, useEffect } from "react";
import { Context } from "..";
import { doc, getDoc, increment, updateDoc, setDoc } from "firebase/firestore";

const Add = () => {
  const ctx = useContext(Context);
  const [addValue, setAddValue] = useState(0);
  const [adding, setAdding] = useState(false);

  // Load user data from Firebase
  useEffect(() => {
    if (ctx.user) {
      const docRef = doc(ctx.db, "Users", ctx.user.uid);

      getDoc(docRef).then((docSnap) => {
        console.log(docSnap);
        if (docSnap.exists()) {
          const data = docSnap.data();
          // Only set Bear Bucks if we don't already have a non-default value
          if (ctx.bearBucks === 1500) {
            ctx.setBearBucks(data.bearBucks || 1500);
          }
        } else {
          // docSnap.data() will be undefined in this case
          console.log("No such document!");
        }
      });
    }
  }, [ctx.user]); // Only run when user changes

  const addHandler = async () => {
    if (!adding) {
      setAdding(true);
      const userRef = doc(ctx.db, "Users", ctx.user.uid);
      
      try {
        // First check if document exists
        const docSnap = await getDoc(userRef);
        
        if (!docSnap.exists()) {
          // Create document with initial Bear Bucks if it doesn't exist
          await setDoc(userRef, {
            bearBucks: 1500 + Number(addValue),
            activeBets: 0,
            wins: 0,
            losses: 0
          });
          ctx.setBearBucks(1500 + Number(addValue));
        } else {
          // Update existing document
          await updateDoc(userRef, { bearBucks: increment(addValue) });
          ctx.setBearBucks(Number(ctx.bearBucks) + Number(addValue));
        }
        
        setAdding(false);
        console.log("Bear Bucks updated successfully");
      } catch (error) {
        console.error("Error updating Bear Bucks:", error);
        alert(`Error updating Bear Bucks: ${error.message}. Please check Firestore permissions.`);
        setAdding(false);
      }
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

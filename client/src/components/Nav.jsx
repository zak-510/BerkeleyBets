import { Link } from "react-router";

const Nav = () => {
  return (
    <div className="w-full flex items-center border-b">
      <div className="p-5 max-w-5xl w-full flex justify-between">
        <Link to="/">Berkeley Bets</Link>
        <div className="flex justify-between gap-5">
          <Link to="/log-in">Log in</Link>
          <Link to="/sign-up">Sign up</Link>
        </div>
      </div>
    </div>
  );
};

export default Nav;

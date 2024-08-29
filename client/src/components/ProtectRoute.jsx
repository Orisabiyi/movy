import PropTypes from "prop-types";

function ProtectRoute({ children }) {
  if (
    !sessionStorage.getItem("accessToken") &&
    !localStorage.getItem("refreshToken")
  )
    return null;

  return <>{children}</>;
}

ProtectRoute.propTypes = {
  children: PropTypes.node.isRequired,
};

export default ProtectRoute;

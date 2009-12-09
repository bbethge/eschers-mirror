public struct Vec2 {
	/**
	 * A 2-D vector.
	 * 
	 * Result arguments may be aliased to inputs unless otherwise specified.
	 */
	public float x;
	public float y;

	public Vec2(float x, float y) {
		this.x = x;
		this.y = y;
	}

	public void add(Vec2 other, out Vec2 result) {
		result.x = x + other.x;
		result.y = y + other.y;
	}

	public void sub(Vec2 other, out Vec2 result) {
		result.x = x - other.x;
		result.y = y - other.y;
	}

	public float dot(Vec2 other) {
		return x*other.x + y*other.y;
	}

	public void scale(float factor, out Vec2 result) {
		result.x = factor * x;
		result.y = factor * y;
	}

	/**
	 * Return the norm/length/magnitude
	 */
	public float norm() {
		return Math.hypotf(x, y);
	}

	/**
	 * Return the norm squared
	 */
	public float norm2() {
		return this.dot(this);
	}

	/**
	 * Rotate 90 degrees clockwise.
	 * result may not be aliased to this.
	 */
	public void rot90(out Vec2 result) {
		result.x = -y;
		result.y = x;
	}

	/**
	 * Rotate angle radians clockwise.
	 * result may not be aliased to this.
	 */
	public void rotate(float angle, out Vec2 result) {
		float sin_angle, cos_angle;
		Math.sincosf(angle, out sin_angle, out cos_angle);
		result.x = x*cos_angle - y*sin_angle;
		result.y = x*sin_angle + y*cos_angle;
	}
}

// vim: set ts=4 sts=4 sw=4 ai noet :

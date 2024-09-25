def generate_call_for_fire():

    return """
    <form method="POST" action="/submit">
        <label>Grid:</label><br>
        <input type="text" name="grid"><br>
        <label>Elevation:</label><br>
        <input type="number" name="elevation"><br>
        <label>Desired Effect:</label><br>
        <select> name="effect" id="desired_effect">
            <option value="high_explosive">High Explosive</option>
            <option value="high_explosive_air_burst">High Explosive Air Burst</option>
            <option value="illumination">Illumination</option>
            <option value="smoke">Smoke</option>
        </select><br><br>
        <label>Number of rounds:</label><br>
        <input type="number" name="number_of_rounds"><br>
        <input type="submit" value="Absenden">
    </form>
    """
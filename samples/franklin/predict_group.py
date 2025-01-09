from daaily.franklin import Client


def main():
    client = Client()
    response = client.predict_product_group(
        image_path="https://storage.googleapis.com/m-on-staging/3100860/product/20306"
        + "985/royal-botania_alura-lounge-set02a_alrl02apbpg_seating_8474ccde.jpeg",
        product_name="Alura Lounge Set02A",
        product_text="The Alura Lounge Set02A is a beautiful outdoor seating set that "
        + "is perfect for any outdoor space. The set includes a sofa, two chairs, and "
        + "a coffee table. The Alura Lounge Set02A is made from high-quality materials "
        + "and is designed to withstand the elements. The set is available in a variety"
        + " of colors and is sure to add style and comfort to your outdoor space.",
    )
    print(response.json())


if __name__ == "__main__":
    main()

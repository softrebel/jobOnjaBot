import pickle
import lxml.html
from lxml.html import Element


def save_cookies(client, filepath):
    # Convert cookies to a dictionary
    cookies_dict = {cookie.name: cookie.value for cookie in client.cookies.jar}
    with open(filepath, "wb") as file:
        pickle.dump(cookies_dict, file)


# Load cookies from a file
def load_cookies(client, filepath):
    with open(filepath, "rb") as file:
        cookies_dict = pickle.load(file)
    # Load cookies into the client
    for name, value in cookies_dict.items():
        client.cookies.set(name, value)


def get_xpath_first_element(node: Element, xpath: str) -> str | None:
    tags = node.xpath(xpath)
    if tags and len(tags) > 0:
        output = tags[0]
        if isinstance(output, str):
            return output.strip()
        return output


def remove_extra_spaces(text: str) -> str:
    return " ".join(text.split())

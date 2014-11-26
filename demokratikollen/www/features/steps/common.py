from behave import *
from nose.tools import *
from selenium.common.exceptions import NoSuchElementException

@given('you browse to the "{page}" page')
def step_impl(context, page):
    if page == 'riksdagen':
        uri = 'riksdagen'
    elif page == 'parties':
        uri = 'partierna'
    context.driver.get("http://127.0.0.1:5555/" + uri)

@then('The response should contain an element "{css_selector}"')
def step_impl(context, css_selector):
    try:
        elements = context.driver.find_element_by_css_selector(css_selector)
    except NoSuchElementException:
        assert False, 'No element found'
    assert True

@given('You browse to the index page')
def step_impl(context):
    context.driver.get("http://127.0.0.1:5555/")

@given('You browse to the about page')
def step_impl(context):
    context.driver.get("http://127.0.0.1:5555/om")

@then('The page title should be "{title}"')
def step_impl(context, title):
    eq_(context.driver.title, title)

@then('No header button should be activated')
def step_impl(context):
    elements = context.driver.find_elements_by_css_selector('ul.menu-items li')

    for element in elements:
        ok_('active' in eq_(element.get_attribute('class')), 'Some header button is activated')

@then('Only the header button "{button_title}" should be activated')
def step_impl(context, button_title):
    elements = context.driver.find_elements_by_css_selector('ul.menu-items li')

    for element in elements:
        if button_title in element.get_attribute('innerHTML'):
            ok_('active' in eq_(element.get_attribute('class')), 'Button is not activated')
        else:
            ok_('active' not in element.get_attribute('class'), 'More than one button active')